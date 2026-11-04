#!/usr/bin/env python3
"""Pick up to 60 "yes" cases from eval 1, spread across what happened next.

Groups:
- removed: the triager removed "not ready" (all of them)
- closed: a maintainer replied, and the PR was closed unmerged within 14
  days of the author comment
- replied: a maintainer replied, and the PR wasn't closed that soon
- no_action: no maintainer action within 14 days (at most 10)

At most 2 cases per PR, and a PR's second case only once every PR in
the group has one. The choice is seeded, so it is repeatable.
"""

import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent
TARGET = {"removed": 99, "closed": 14, "no_action": 10}
TOTAL = 60
MAX_PER_PR = 2


def ptime(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


cases = json.loads((EVAL / "data/eval1_cases.json").read_text())
states = json.loads((EVAL / "data/pr_state_now.json").read_text())
groups: dict[str, list[dict]] = defaultdict(list)
for case in cases:
    key = json.loads((EVAL / f"data/eval1_keys/{case['id']}.json").read_text())
    if key["answer"] != "yes":
        continue
    next_step = case["what_happened_next"]
    state = states[str(case["pr"])]
    if next_step.startswith("triager removed"):
        group = "removed"
    elif next_step.startswith("no maintainer action"):
        group = "no_action"
    elif (
        state["closed_at"]
        and not state["merged_at"]
        and ptime(state["closed_at"]) - ptime(case["author_comment"]["created_at"])
        <= timedelta(days=14)
    ):
        group = "closed"
    else:
        group = "replied"
    case["group"] = group
    groups[group].append(case)

print({g: len(v) for g, v in groups.items()})
rng = random.Random(2)
chosen: list[dict] = []
per_pr: Counter[int] = Counter()


def take(group: str, limit: int) -> None:
    pool = groups[group][:]
    rng.shuffle(pool)
    taken = 0
    for round_limit in range(1, MAX_PER_PR + 1):
        for case in pool:
            if taken >= limit or len(chosen) >= TOTAL:
                return
            if case in chosen or per_pr[case["pr"]] >= round_limit:
                continue
            chosen.append(case)
            per_pr[case["pr"]] += 1
            taken += 1


for group in ("removed", "closed", "no_action"):
    take(group, TARGET[group])
take("replied", TOTAL - len(chosen))
chosen.sort(key=lambda c: c["id"])
(EVAL / "cases.json").write_text(json.dumps(chosen, indent=1))
print(len(chosen), Counter(c["group"] for c in chosen), len({c["pr"] for c in chosen}))
