# Reviewer-suggestion eval (eval3): not run, blocked on GitHub access

**Status: no cases, no bot runs, no scores.** This run stopped before any
model calls.

## Why

The case definition needs each PR's issue timeline (when "maintainer
review" was added, and when the assignee was set). It also needs the PR as
of that moment: comments, labels and files. All of that comes from the
GitHub REST API for zulip/zulip, and this session can't read it:

- The session only has `shubham-padia/zulip` attached. Attaching
  `zulip/zulip` was refused because two repositories with the same name
  can't share one session (they'd be checked out in the same directory).
- Direct API calls (`/repos/zulip/zulip/issues/N/timeline`) return 403
  "GitHub access to this repository is not enabled for this session".
- Only the search API works. It shows current labels and assignees, not
  when they changed, so it can't find the hand-off moment or rebuild the
  PR as of it.

I didn't fill the gap with guessed hand-off times or made-up results.

## What is done

- `prompts/v1_file_history.md`: ranks by who changed these files, then by
  who is in the discussion.
- `prompts/v2_area_activity.md`: decides the area first (labels, title
  prefix, linked issue), then prefers maintainers already engaged with the
  work, then recent activity in the area.
- `cache/search_maintainer_review_prs.jsonl`: all 174 PRs created
  2026-05-01..2026-10-31 that have "maintainer review" now.
- `candidates_current_state.json`: 126 of them have a non-maintainer
  author and an assignee who isn't the author. This is a superset guess
  only. It misses PRs whose label was later removed, and it doesn't check
  the 1-hour rule.

## To run it

Start a new session with `zulip/zulip` as its source, not the fork. From
there the timelines and PR data can be read, and the fork branch can be
fetched for the bot code. Upstream git refs (`refs/pull/N/head`) are
already readable over git, so file lists and history could also come from
git.
