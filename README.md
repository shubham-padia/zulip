# Triage bot eval 3 data: reviewer suggestion

- `cases.json`: 100 most recent contributor PRs (created 2026-05..10) that a maintainer handed off with "maintainer review", with an assignee (not the author) set within 1 hour. `assignee` is the ground truth; `cutoff` is 1 second before the earlier of the label and the assignment.
- `inputs/<pr>.md`: the bot input for the PR as of the cutoff (tools/triage_bot assemble.py output, built with eval 2's cutoff gatherer). Ends with "Core contributors who changed these files in the last year" (git author names).
- `inputs/<pr>.meta.json`: cutoff head, files, and file authors (name, commits).
- `handoff_history.json`: all 456 hand-offs (maintainer/integration/priority integration review + assignee within 1 hour) on contributor PRs created in 2026, with label, assignee, times and the PR's changed files. For baseline (b).
- `maintainers.txt` / `maintainer_names.tsv`: MAINTAINERS logins from gather.py, and their GitHub display names (to map git author names to logins).
- `gather3.py`: how the inputs were built.
