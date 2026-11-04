#!/usr/bin/env python3
"""Gather eval 2 inputs: a "not ready" PR as of an author's comment.

  gather_case.py CASE_ID [CASE_ID ...]

CASE_ID is an id from eval2/cases.json ("<pr>-<comment id>"). For each
case, writes under eval2/:

  inputs/<case>.cutoff.md  bot input as of the author's comment: the
                           assemble.py output, then a "Second look"
                           section with the maintainer feedback, the
                           code changes since it, and the new comment
  inputs/<case>.all.md     the PR with no cutoff (for the key): the
                           assemble.py output from gather.gather() plus
                           a "Later events" section
  gather/<case>.meta.json  how the cutoff view was built, to check it
                           by hand

Existing outputs are skipped, so a rerun only does missing work.

The cutoff is the author comment's time. The cutoff view uses the
lookups in tools/triage_bot/gather.py, with these changes (the same as
the earlier evals' cutoff gatherer):
- title and description as of the cutoff (renamed events, GraphQL
  userContentEdits);
- comments, labels, assignees, review requests and draft state from
  timeline events up to the cutoff; linked items and earlier attempts
  likewise, with their state at the cutoff, and only if they existed;
- GitHub searches (similar items, author history) limited with
  created:<cutoff; their state at the cutoff;
- CZO search hits and thread messages only from before the cutoff;
- the PR head at the cutoff from Zulip CI runs and force-push events;
  files, commits and size at that head (compare against main);
- CI only if the PR head is unchanged since the cutoff, else unknown.
"""

import fcntl
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from itertools import islice
from pathlib import Path

import requests

EVAL = Path(__file__).resolve().parent.parent
ZULIP = EVAL.parent
sys.path.insert(0, str(ZULIP))
os.environ.setdefault(
    "GH_TOKEN", subprocess.check_output(["gh", "auth", "token"], text=True).strip()
)

from tools.triage_bot import assemble as A  # noqa: E402
from tools.triage_bot import gather as G  # noqa: E402

INPUTS = EVAL / "inputs"
META = EVAL / "gather"
REPO = G.REPO
# The author's comment itself is part of the cutoff view.
CUTOFF_MARGIN = timedelta(seconds=1)
FEEDBACK_CHARS = 4000
AUTHOR_COMMENT_CHARS = 4000

ORIGINAL_SEARCH = G.search_issues
ORIGINAL_CZO_GET = G.czo_get
ORIGINAL_FETCH_CZO_THREAD = G.fetch_czo_thread

# Set while gathering as of a cutoff; the patched lookups read it.
CUTOFF: datetime | None = None
# Issue objects returned by searches, by number, to recompute their state.
SEARCHED: dict[int, object] = {}



def iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ptime(s: str | None) -> datetime | None:
    return G.parse_github_time(s) if s else None


def known(t: datetime | None) -> bool:
    return CUTOFF is None or (t is not None and t <= CUTOFF)


# --- patched lookups ---


SEARCH_LOCK = EVAL / "logs" / "search.lock"
# GitHub allows 30 searches a minute; gatherers run in parallel processes,
# so they share one spacing through a locked file.
SEARCH_SPACING = 2.2


def wait_for_search_slot() -> None:
    SEARCH_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with SEARCH_LOCK.open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        last = float(f.read().strip() or 0)
        wait = last + SEARCH_SPACING - time.time()
        if wait > 0:
            time.sleep(wait)
        f.seek(0)
        f.truncate()
        f.write(str(time.time()))
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)


def search_issues(query: str, limit: int, newest_first: bool = True):
    wait_for_search_slot()
    if CUTOFF is not None:
        if "is:merged" in query:
            query = query.replace("is:merged", f"merged:<{iso(CUTOFF)}")
        query += f" created:<{iso(CUTOFF)}"
    results = ORIGINAL_SEARCH(query, limit, newest_first)
    for r in results:
        SEARCHED[r.number] = r
    return results


def czo_get(narrow, before, anchor="newest", after=0):
    is_search = any(term.get("operator") == "search" for term in narrow)
    if CUTOFF is None or not is_search:
        return ORIGINAL_CZO_GET(narrow, before, anchor, after)
    # The newest hits may all be from after the cutoff; read more, keep
    # those before it.
    result = ORIGINAL_CZO_GET(narrow, max(before, 1000), anchor, after)
    messages = [m for m in result.get("messages", []) if m["timestamp"] <= CUTOFF.timestamp()]
    return {**result, "messages": messages[-before:]}


def fetch_czo_thread(channel_id: int, topic: str) -> G.CzoThread:
    if CUTOFF is None:
        return ORIGINAL_FETCH_CZO_THREAD(channel_id, topic)
    result = ORIGINAL_CZO_GET(G.topic_narrow(channel_id, topic), before=5000)
    all_messages = result.get("messages", [])
    messages = [m for m in all_messages if m["timestamp"] <= CUTOFF.timestamp()]
    shown = messages[-G.CZO_MESSAGES_SHOWN :]
    # A topic resolved after the cutoff wasn't resolved at the cutoff.
    resolved_later = topic.startswith("✔ ") and any(
        m["timestamp"] > CUTOFF.timestamp() for m in all_messages
    )
    return G.CzoThread(
        channel_id=channel_id,
        channel=all_messages[0]["display_recipient"] if all_messages else "",
        topic=topic.removeprefix("✔ ") if resolved_later else topic,
        messages=[G.czo_message(m) for m in shown],
        found_oldest=result.get("found_oldest", True) and len(shown) == len(messages),
    )


G.search_issues = search_issues
G.czo_get = czo_get
G.fetch_czo_thread = fetch_czo_thread


# --- GitHub helpers ---


def graphql(query: str, **variables: object) -> dict:
    r = G.czo_session.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json().get("data") or {}


EDITS_QUERY = """query($owner:String!,$name:String!,$n:Int!){repository(owner:$owner,name:$name){
issueOrPullRequest(number:$n){
 ... on Issue {body userContentEdits(first:100){nodes{editedAt diff}}}
 ... on PullRequest {body userContentEdits(first:100){nodes{editedAt diff}}}}}}"""


def body_at(repo: str, number: int, current: str) -> tuple[str, int, int]:
    """The description as of the cutoff, and (edits, edits after the cutoff)."""
    owner, name = repo.split("/")
    node = (graphql(EDITS_QUERY, owner=owner, name=name, n=number).get("repository") or {}).get(
        "issueOrPullRequest"
    ) or {}
    edits = [e for e in (node.get("userContentEdits") or {}).get("nodes", []) if e and e.get("diff") is not None]
    if CUTOFF is None or not edits:
        return current, len(edits), 0
    edits.sort(key=lambda e: e["editedAt"])
    before = [e for e in edits if ptime(e["editedAt"]) <= CUTOFF]
    later = len(edits) - len(before)
    if later == 0:
        return current, len(edits), 0
    # The oldest entry holds the text as first posted.
    return (before[-1] if before else edits[0])["diff"] or "", len(edits), later


def event_time(e: dict) -> datetime | None:
    return ptime(e.get("created_at") or e.get("submitted_at"))


def title_at(events: list[dict], current: str) -> str:
    if CUTOFF is None:
        return current
    for e in events:
        if e.get("event") == "renamed" and not known(event_time(e)):
            return e["rename"]["from"]
    return current


def labels_assignees_at(events: list[dict]) -> tuple[list[str], list[str], list[str]]:
    labels: dict[str, None] = {}
    assignees: dict[str, None] = {}
    reviewers: dict[str, None] = {}
    for e in events:
        if not known(event_time(e)):
            continue
        kind = e.get("event")
        if kind == "labeled":
            labels[e["label"]["name"]] = None
        elif kind == "unlabeled":
            labels.pop(e["label"]["name"], None)
        elif kind == "assigned":
            assignees[G.user_login(e.get("assignee"))] = None
        elif kind == "unassigned":
            assignees.pop(G.user_login(e.get("assignee")), None)
        elif kind == "review_requested" and e.get("requested_reviewer"):
            reviewers[G.user_login(e.get("requested_reviewer"))] = None
        elif kind == "review_request_removed" and e.get("requested_reviewer"):
            reviewers.pop(G.user_login(e.get("requested_reviewer")), None)
    return list(labels), list(assignees), list(reviewers)


def state_at(issue, events: list[dict] | None = None) -> G.ItemState:
    if CUTOFF is None:
        return G.item_state(issue)
    merged_at = None
    if G.item_kind(issue) == "pr" and issue.pull_request is not None:
        merged_at = issue.pull_request.merged_at
    if merged_at is not None and merged_at <= CUTOFF:
        return "merged"
    if events is not None:
        state: G.ItemState = "open"
        for e in events:
            if known(event_time(e)) and e.get("event") in ("closed", "reopened"):
                state = "closed" if e["event"] == "closed" else "open"
        return state
    closed_at = issue.closed_at
    return "closed" if closed_at is not None and closed_at <= CUTOFF and issue.state == "closed" else "open"


def comments_at(events: list[dict]) -> list[G.Comment]:
    return [c for c in G.comments_from_timeline(events) if known(c.created_at)]


def referencing_prs_at(events: list[dict]) -> list[int]:
    return G.referencing_prs_from_timeline([e for e in events if known(event_time(e))])


def linked_item_at(number: int, repo: str = REPO, *, with_files: bool = False) -> G.LinkedItem | None:
    """G.fetch_linked_item as of the cutoff; None if it didn't exist then."""
    try:
        issue = G.repository(repo).get_issue(number).complete()
    except G.UnknownObjectException:
        return None
    if not known(issue.created_at):
        return None
    events = G.fetch_timeline(issue)
    labels, assignees, _ = labels_assignees_at(events)
    body, _, _ = body_at(repo, number, issue.body or "")
    item = G.LinkedItem(
        number=number,
        repo=repo,
        ref=f"#{number}" if repo == REPO else f"{repo}#{number}",
        kind=G.item_kind(issue),
        title=title_at(events, issue.title),
        author=G.named_user_login(issue.user),
        author_association=issue.author_association,
        created_at=issue.created_at,
        state=state_at(issue, events),
        labels=labels if CUTOFF is not None else [label.name for label in issue.labels],
        assignees=assignees if CUTOFF is not None else [a.login for a in issue.assignees],
        body=body,
        comments=comments_at(events),
        referencing_prs=referencing_prs_at(events),
    )
    if item.kind == "pr" and with_files:
        pr_files = G.repository(repo).get_pull(number).get_files()
        item.files = [f.filename for f in islice(pr_files, G.MAX_PR_FILES)]
    return item


def find_attempts_at(item: G.Item, linked: list[G.LinkedItem], comments: list[G.Comment]) -> list[G.Attempt]:
    """G.find_attempts, with each attempt as of the cutoff."""
    attempt_numbers = {
        n for li in linked if li.kind == "issue" for n in li.referencing_prs if n != item.number
    }
    author_comments = " ".join(c.body for c in comments if c.author == item.author)
    mention_text = item.body + " " + author_comments
    attempts = []
    for n in sorted(attempt_numbers)[-G.MAX_ATTEMPTS :]:
        pr = linked_item_at(n, with_files=True)
        if not pr:
            continue
        maintainer_comments = [c for c in pr.comments if c.is_maintainer]
        attempts.append(
            G.Attempt(
                pr=pr,
                last_maintainer_comment=maintainer_comments[-1] if maintainer_comments else None,
                mentioned_in_item=bool(re.search(rf"#{n}\b|/pull/{n}\b", mention_text)),
                same_author=pr.author == item.author,
                files_shared=sorted(set(pr.files) & set(item.files)),
            )
        )
    return attempts


def fix_similar_states(similar: list[G.SimilarItem]) -> list[G.SimilarItem]:
    return [replace(s, state=state_at(SEARCHED[s.number])) if s.number in SEARCHED else s for s in similar]


def author_history_at(author: str, number: int) -> G.AuthorHistory:
    """G.fetch_author_history with searches limited to the cutoff and states as of it."""
    merged = search_issues(f"repo:{REPO} type:pr is:merged author:{author}", 1)

    def entries(query: str, limit: int) -> list[G.AuthorHistoryEntry]:
        results = search_issues(f"repo:{REPO} {query} author:{author}", limit + 1)
        out = []
        for r in [r for r in results if r.number != number][:limit]:
            state = state_at(r)
            out.append(
                G.AuthorHistoryEntry(
                    number=r.number,
                    title=r.title,
                    created_at=r.created_at,
                    state=state,
                    closing_comment=G.fetch_closing_comment(r) if state == "closed" else None,
                )
            )
        return out

    return G.AuthorHistory(
        has_merged_pr=bool(merged),
        prs=entries("type:pr", G.AUTHOR_PRS_SHOWN),
        issues=entries("type:issue", G.AUTHOR_ISSUES_SHOWN),
    )


def file_authors_at(files: list[str]) -> list[G.FileAuthor]:
    """G.find_file_authors with the git log windows ending at the cutoff."""
    if not files or CUTOFF is None:
        return G.find_file_authors(files)

    def shortlog(days: int, *paths: str) -> list[str]:
        since = iso(CUTOFF - timedelta(days=days))
        return subprocess.check_output(
            ["git", "shortlog", "-sn", f"--since={since}", f"--until={iso(CUTOFF)}", "HEAD", "--", *paths],
            cwd=G.ZULIP_PATH,
            text=True,
        ).splitlines()

    core = {line.split("\t")[1] for line in shortlog(730)[: G.CORE_CONTRIBUTOR_COUNT]}
    authors = []
    for line in shortlog(365, *files):
        count, name = line.split("\t")
        if name in core:
            authors.append(G.FileAuthor(name=name, commits=int(count)))
    return authors[: G.FILE_AUTHORS_SHOWN]


# --- cutoff ---


def first_attempt(run) -> tuple[datetime, str | None]:
    """When the run's first attempt completed, and its conclusion."""
    if run.run_attempt and run.run_attempt > 1:
        _, data = G.github().requester.requestJsonAndCheck("GET", f"{run.url}/attempts/1")
        return G.parse_github_time(data["updated_at"]), data.get("conclusion")
    return run.updated_at, run.conclusion


def ci_runs(pr, events: list[dict]) -> list:
    """Zulip CI pull_request runs for this PR, oldest first."""
    runs = []
    if pr.head.repo is not None:
        for run in islice(
            G.repository().get_workflow(G.CI_WORKFLOW_FILE).get_runs(
                branch=pr.head.ref, event="pull_request", created=f">={iso(pr.created_at - timedelta(minutes=10))}"
            ),
            200,
        ):
            if run.head_repository is not None and run.head_repository.full_name == pr.head.repo.full_name:
                runs.append(run)
    if not runs:
        shas = {pr.head.sha} | {e["sha"] for e in events if e.get("event") == "committed" and e.get("sha")}
        seen = set()
        for sha in shas:
            for run in G.fetch_ci_workflow_runs(sha):
                if run.id not in seen:
                    seen.add(run.id)
                    runs.append(run)
    return sorted(runs, key=lambda run: run.created_at)



FORCE_PUSH_QUERY = """query($n:Int!){repository(owner:"zulip",name:"zulip"){pullRequest(number:$n){
timelineItems(itemTypes:[HEAD_REF_FORCE_PUSHED_EVENT], first:100){nodes{
 ... on HeadRefForcePushedEvent{createdAt afterCommit{oid} beforeCommit{oid}}}}}}}"""


def push_history(pr, events: list[dict]) -> list[tuple[datetime, str, str]]:
    """(time, sha, source) for each known head of the PR, oldest first.

    Each push starts a Zulip CI run, and each force push leaves a
    timeline event; a plain push without a CI run is missed.
    """
    history = [(run.created_at, run.head_sha, "ci run") for run in ci_runs(pr, events)]
    data = graphql(FORCE_PUSH_QUERY, n=pr.number)
    nodes = (((data.get("repository") or {}).get("pullRequest") or {}).get("timelineItems") or {}).get(
        "nodes", []
    )
    for node in nodes:
        if node and node.get("afterCommit"):
            history.append((ptime(node["createdAt"]), node["afterCommit"]["oid"], "force push"))
    history.sort(key=lambda entry: entry[0])
    return history


def head_at(history: list[tuple[datetime, str, str]], when: datetime) -> str | None:
    before = [sha for t, sha, _ in history if t <= when]
    return before[-1] if before else None


def shape_at(sha: str) -> dict:
    """Files, commits and size of the PR with the given head."""
    cmp = G.repository().compare("main", sha)
    files = list(islice(cmp.files, G.MAX_PR_FILES))
    return {
        "files": [f.filename for f in files],
        "additions": sum(f.additions for f in files),
        "deletions": sum(f.deletions for f in files),
        "commits": [c.commit.message.partition("\n")[0] for c in cmp.commits],
    }


def set_shape(item: G.Item, shape: dict) -> None:
    item.files = shape["files"]
    item.changed_files = len(shape["files"])
    item.additions, item.deletions = shape["additions"], shape["deletions"]
    item.commits = shape["commits"]


def draft_at(events: list[dict], draft_now: bool) -> bool:
    toggles = [e for e in events if e.get("event") in ("ready_for_review", "convert_to_draft")]
    if not toggles:
        return draft_now
    draft = toggles[0]["event"] == "ready_for_review"
    for e in toggles:
        if known(event_time(e)):
            draft = e["event"] == "convert_to_draft"
    return draft


def not_ready_label_event(events: list[dict]) -> dict | None:
    added = [
        e
        for e in events
        if e.get("event") == "labeled"
        and e["label"]["name"] == "not ready"
        and known(event_time(e))
    ]
    return added[-1] if added else None


def changes_lines(then: dict | None, now: dict, head_then: str | None, head_now: str | None, pushes: int) -> list[str]:
    if head_now is None or head_then is None:
        return ["Unknown: the PR's head commit at one of these times couldn't be found."]
    if head_then == head_now:
        return ["None: the head commit is the same as when the feedback was given (no new push)."]
    lines = [f"New pushes since the feedback: {pushes}."]
    if then is None:
        lines.append("The commits and files at the time of the feedback couldn't be read.")
        return lines
    lines.append(
        f"Size then: +{then['additions']}/-{then['deletions']} in {len(then['files'])} files. "
        f"Size now: +{now['additions']}/-{now['deletions']} in {len(now['files'])} files."
    )
    if then["commits"] != now["commits"]:
        lines.append("Commits then:")
        lines.extend(f"- {c}" for c in then["commits"][: A.COMMITS_SHOWN])
        lines.append("Commits now:")
        lines.extend(f"- {c}" for c in now["commits"][: A.COMMITS_SHOWN])
    else:
        lines.append("Commit messages: unchanged.")
    added = sorted(set(now["files"]) - set(then["files"]))
    removed = sorted(set(then["files"]) - set(now["files"]))
    if added:
        lines.append("Files added to the PR: " + ", ".join(added[: A.FILES_SHOWN]))
    if removed:
        lines.append("Files no longer in the PR: " + ", ".join(removed[: A.FILES_SHOWN]))
    if not added and not removed:
        lines.append("Same files as before.")
    return lines


def second_look_lines(
    case: dict, label_event: dict | None, feedback: G.Comment | None, changes: list[str]
) -> list[str]:
    lines = ["## Second look", ""]
    if label_event is not None:
        lines.append(
            f'"not ready" label added by {G.user_login(label_event.get("actor"))} '
            f"on {event_time(label_event):%Y-%m-%d}."
        )
    else:
        lines.append('"not ready" label: on the PR (when it was added is unknown).')
    lines.append("")
    lines.append("### The maintainer feedback the author is answering")
    if feedback:
        lines.append(
            f"[{feedback.author}, maintainer, {feedback.created_at:%Y-%m-%d}, {feedback.kind}]\n"
            + A.clip(feedback.body, FEEDBACK_CHARS)
        )
    else:
        lines.append("(No maintainer comment before the author's comment; only the label.)")
    lines.extend(["", "### Code changes between that feedback and the author's comment"])
    lines.extend(changes)
    comment = case["author_comment"]
    lines.extend(
        [
            "",
            "### The author's new comment (this is what the second look is about)",
            f"[{case['author']}, PR author, {comment['created_at'][:16].replace('T', ' ')} UTC]\n"
            + A.clip(comment["body"], AUTHOR_COMMENT_CHARS),
        ]
    )
    return lines


def gather_at_cutoff(case: dict) -> tuple[str, dict]:
    global CUTOFF
    number = case["pr"]
    issue = G.repository().get_issue(number).complete()
    events = G.fetch_timeline(issue)
    pr = G.repository().get_pull(number)
    cutoff = ptime(case["author_comment"]["created_at"]) + CUTOFF_MARGIN
    meta: dict = {"case": case["id"], "cutoff": iso(cutoff)}
    history = push_history(pr, events)
    meta["pushes"] = [(iso(t), sha[:10], source) for t, sha, source in history]
    CUTOFF = cutoff
    SEARCHED.clear()
    try:
        item = G.fetch_item(number)
        assert item is not None
        meta["head_now"] = item.head_sha
        item.title = title_at(events, item.title)
        item.body, edits, later = body_at(REPO, number, item.body)
        meta["body_edits"], meta["body_edits_after_cutoff"] = edits, later
        meta["title_now"], meta["title_at_cutoff"] = issue.title, item.title
        meta["labels_now"], meta["assignees_now"] = item.labels, item.assignees
        item.labels, item.assignees, item.review_requested = labels_assignees_at(events)
        item.draft = draft_at(events, item.draft)

        head_cutoff = head_at(history, cutoff)
        meta["head_at_cutoff"] = head_cutoff
        shape_now = None
        if head_cutoff and head_cutoff != item.head_sha:
            try:
                shape_now = shape_at(head_cutoff)
                set_shape(item, shape_now)
                meta["pr_shape"] = f"from compare main...{head_cutoff[:10]}"
            except Exception as e:  # noqa: BLE001
                meta["pr_shape"] = f"compare failed ({e!r}); current shape"
        else:
            meta["pr_shape"] = "current head = cutoff head" if head_cutoff else "cutoff head unknown; current shape"
        if shape_now is None:
            shape_now = {
                "files": item.files,
                "additions": item.additions,
                "deletions": item.deletions,
                "commits": item.commits,
            }
        ci: list[str] | None = None
        if head_cutoff and head_cutoff == item.head_sha:
            ci = G.fetch_ci_conclusions(item.head_sha)
            meta["ci"] = "head unchanged since cutoff; current check runs"
        else:
            meta["ci"] = "head changed since cutoff (or unknown); CI unknown"

        label_event = not_ready_label_event(events)
        comments = comments_at(events)
        author_time = ptime(case["author_comment"]["created_at"])
        maintainer_comments = [
            c
            for c in comments
            if c.is_maintainer and not c.is_bot and c.author != item.author and c.created_at < author_time
        ]
        feedback = maintainer_comments[-1] if maintainer_comments else None
        meta["feedback"] = f"{feedback.author} {iso(feedback.created_at)}" if feedback else None
        if feedback:
            feedback_time = feedback.created_at
        elif label_event is not None:
            feedback_time = event_time(label_event)
        else:
            feedback_time = None
        head_feedback = head_at(history, feedback_time) if feedback_time else None
        meta["head_at_feedback"] = head_feedback
        shape_then = None
        if head_feedback and head_cutoff and head_feedback != head_cutoff:
            try:
                shape_then = shape_at(head_feedback)
            except Exception as e:  # noqa: BLE001
                meta["shape_then"] = f"compare failed ({e!r})"
        pushes = len(
            {sha for t, sha, _ in history if feedback_time and feedback_time < t <= cutoff}
        )
        changes = changes_lines(shape_then, shape_now, head_feedback, head_cutoff, pushes)

        meta["comments_total"] = len(G.comments_from_timeline(events))
        meta["comments_at_cutoff"] = len(comments)
        text = item.title + "\n" + item.body
        refs = [r for r in dict.fromkeys(G.linked_item_refs(text)) if r != (REPO, number)]
        linked = [li for li in (linked_item_at(n, repo) for repo, n in refs[: G.MAX_LINKED_ITEMS]) if li]
        attempts = find_attempts_at(item, linked, comments)
        similar = fix_similar_states(G.find_similar(number, item.title))
        texts = [item.body] + [c.body for c in comments]
        for related in [*linked, *(a.pr for a in attempts)]:
            texts += [related.body] + [c.body for c in related.comments]
        thread, unread = G.find_czo_thread(number, texts, linked, [a.pr.number for a in attempts])
        history_entries = author_history_at(item.author, number)
        if item.author_association == "CONTRIBUTOR" and not history_entries.has_merged_pr:
            item.author_association = "FIRST_TIME_CONTRIBUTOR"
            meta["author_association"] = "CONTRIBUTOR now, no merged PR before cutoff"
        gathered = G.GatheredItem(
            item=item,
            author_name=G.fetch_user_name(item.author),
            comments=comments,
            linked=linked,
            attempts=attempts,
            similar=similar,
            czo_thread=thread,
            czo_unread_links=unread,
            author_history=history_entries,
            ci_conclusions=ci,
            file_authors=file_authors_at(item.files),
        )
        text = A.assemble(gathered)
        text += "\n" + "\n".join(second_look_lines(case, label_event, feedback, changes)) + "\n"
    finally:
        CUTOFF = None
    return text, meta


def later_events(number: int) -> list[str]:
    issue = G.repository().get_issue(number).complete()
    events = G.fetch_timeline(issue)
    lines = [
        f"State now: {G.item_state(issue)}"
        + (f" ({issue.state_reason})" if getattr(issue, "state_reason", None) else "")
        + (f", closed {issue.closed_at:%Y-%m-%d} by {G.named_user_login(issue.closed_by)}" if issue.closed_at else ""),
    ]
    for e in events:
        kind = e.get("event")
        t = event_time(e)
        when = f"{t:%Y-%m-%d %H:%M}" if t else "?"
        actor = G.user_login(e.get("actor"))
        if kind in ("labeled", "unlabeled"):
            lines.append(f"- {when} {actor} {kind} {e['label']['name']!r}")
        elif kind in ("assigned", "unassigned"):
            lines.append(f"- {when} {actor} {kind} {G.user_login(e.get('assignee'))}")
        elif kind in ("review_requested", "review_request_removed"):
            lines.append(f"- {when} {actor} {kind} {G.user_login(e.get('requested_reviewer'))}")
        elif kind in ("closed", "reopened", "merged", "ready_for_review", "convert_to_draft", "marked_as_duplicate", "renamed", "head_ref_force_pushed"):
            extra = f" {e['rename']['from']!r} -> {e['rename']['to']!r}" if kind == "renamed" else ""
            lines.append(f"- {when} {actor} {kind}{extra}")
        elif kind == "cross-referenced":
            src = (e.get("source") or {}).get("issue") or {}
            if src.get("number"):
                lines.append(f"- {when} referenced from #{src['number']}: {src.get('title', '')}")
    return lines




def main() -> None:
    INPUTS.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    cases = {c["id"]: c for c in json.loads((EVAL / "cases.json").read_text())}
    for case_id in sys.argv[1:]:
        case = cases[case_id]
        cut_file = INPUTS / f"{case_id}.cutoff.md"
        all_file = INPUTS / f"{case_id}.all.md"
        meta_file = META / f"{case_id}.meta.json"
        try:
            if not (cut_file.exists() and meta_file.exists()):
                text, meta = gather_at_cutoff(case)
                cut_file.write_text(text)
                meta_file.write_text(json.dumps(meta, indent=1))
                print(f"{case_id}: cutoff {meta['cutoff']} ({meta['pr_shape']})", file=sys.stderr)
            if not all_file.exists():
                item = G.fetch_item(case["pr"])
                assert item is not None
                text = A.assemble(G.gather(item))
                text += (
                    "\n## Later events (everything on the PR's timeline, up to now)\n"
                    + "\n".join(later_events(case["pr"]))
                    + "\n"
                )
                all_file.write_text(text)
                print(f"{case_id}: all facts gathered", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"{case_id}: FAILED {e!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
