#!/usr/bin/env python3
"""Build eval 3 inputs: each PR as of just before its hand-off.

  gather3.py PR [PR ...]

Reuses eval 2's cutoff gatherer (gather_case.py), without its
second-look section.  Writes inputs/<pr>.md and inputs/<pr>.meta.json;
existing outputs are skipped.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVAL2_SCRIPTS = Path("/home/zulipdev/zulip/.claude/worktrees/agent-a1c9249fe4d0d2733/eval2/scripts")
sys.path.insert(0, str(EVAL2_SCRIPTS))

import gather_case as gc  # noqa: E402

A, G = gc.A, gc.G
CASES = {c["pr"]: c for c in json.loads((ROOT / "cases.json").read_text())}


def gather_before_handoff(case: dict) -> tuple[str, dict]:
    number = case["pr"]
    issue = G.repository().get_issue(number).complete()
    events = G.fetch_timeline(issue)
    pr = G.repository().get_pull(number)
    cutoff = gc.ptime(case["cutoff"])
    meta: dict = {"pr": number, "cutoff": gc.iso(cutoff)}
    history = gc.push_history(pr, events)
    gc.CUTOFF = cutoff
    gc.SEARCHED.clear()
    try:
        item = G.fetch_item(number)
        assert item is not None
        item.title = gc.title_at(events, item.title)
        item.body, _, _ = gc.body_at(G.REPO, number, item.body)
        item.labels, item.assignees, item.review_requested = gc.labels_assignees_at(events)
        item.draft = gc.draft_at(events, item.draft)
        head_cutoff = gc.head_at(history, cutoff)
        meta["head_at_cutoff"] = head_cutoff
        if head_cutoff and head_cutoff != item.head_sha:
            try:
                gc.set_shape(item, gc.shape_at(head_cutoff))
                meta["pr_shape"] = "compare at cutoff head"
            except Exception as e:  # noqa: BLE001
                meta["pr_shape"] = f"compare failed ({e!r}); current shape"
        ci = None
        if head_cutoff and head_cutoff == item.head_sha:
            ci = G.fetch_ci_conclusions(item.head_sha)
        comments = gc.comments_at(events)
        text = item.title + "\n" + item.body
        refs = [r for r in dict.fromkeys(G.linked_item_refs(text)) if r != (G.REPO, number)]
        linked = [li for li in (gc.linked_item_at(n, repo) for repo, n in refs[: G.MAX_LINKED_ITEMS]) if li]
        attempts = gc.find_attempts_at(item, linked, comments)
        similar = gc.fix_similar_states(G.find_similar(number, item.title))
        texts = [item.body] + [c.body for c in comments]
        for related in [*linked, *(a.pr for a in attempts)]:
            texts += [related.body] + [c.body for c in related.comments]
        thread, unread = G.find_czo_thread(number, texts, linked, [a.pr.number for a in attempts])
        author_history = gc.author_history_at(item.author, number)
        file_authors = gc.file_authors_at(item.files)
        meta["file_authors"] = [(fa.name, fa.commits) for fa in file_authors]
        meta["files"] = item.files
        gathered = G.GatheredItem(
            item=item,
            author_name=G.fetch_user_name(item.author),
            comments=comments,
            linked=linked,
            attempts=attempts,
            similar=similar,
            czo_thread=thread,
            czo_unread_links=unread,
            author_history=author_history,
            ci_conclusions=ci,
            file_authors=file_authors,
        )
        return A.assemble(gathered), meta
    finally:
        gc.CUTOFF = None


def main() -> None:
    out = ROOT / "inputs"
    out.mkdir(exist_ok=True)
    for arg in sys.argv[1:]:
        number = int(arg)
        if (out / f"{number}.md").exists():
            continue
        try:
            text, meta = gather_before_handoff(CASES[number])
        except Exception as e:  # noqa: BLE001
            print(f"FAILED #{number}: {e!r}", flush=True)
            continue
        (out / f"{number}.meta.json").write_text(json.dumps(meta, indent=1))
        (out / f"{number}.md").write_text(text)
        print(f"ok #{number}", flush=True)


if __name__ == "__main__":
    main()
