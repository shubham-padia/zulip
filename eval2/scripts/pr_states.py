#!/usr/bin/env python3
"""Fetch the current state of every PR with a "yes" case, for case selection."""

import json
import subprocess
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent
cases = json.loads((EVAL / "data/eval1_cases.json").read_text())
yes = [
    c
    for c in cases
    if json.loads((EVAL / f"data/eval1_keys/{c['id']}.json").read_text())["answer"] == "yes"
]
out = EVAL / "data/pr_state_now.json"
info = json.loads(out.read_text()) if out.exists() else {}
JQ = (
    "{state, closed_at, closed_by: .closed_by.login, merged_at: .pull_request.merged_at,"
    " labels: [.labels[].name], assignees: [.assignees[].login]}"
)
for n in sorted({c["pr"] for c in yes}):
    if str(n) in info:
        continue
    raw = subprocess.run(
        ["gh", "api", f"repos/zulip/zulip/issues/{n}", "--jq", JQ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    info[str(n)] = json.loads(raw)
out.write_text(json.dumps(info, indent=1))
print(len(yes), len(info))
