#!/usr/bin/env python3
"""Score each bot run against the Opus key, and show how the key lines
up with what maintainers did next."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def answers(run: str) -> dict[str, str]:
    return {
        path.stem: json.loads(path.read_text())["answer"]
        for path in (ROOT / "results" / run).glob("*.json")
    }


def main() -> None:
    cases = {case["id"]: case for case in json.loads((ROOT / "cases.json").read_text())}
    key = answers("key")
    print(f"Key: {Counter(key.values())}")
    print("Key vs what happened next:")
    for (outcome, answer), count in sorted(
        Counter((cases[c]["what_happened_next"], a) for c, a in key.items()).items()
    ):
        print(f"  {outcome:45} key={answer:8} {count}")

    print("\nRun      agree  yes->no  no->yes  unparsed  cost")
    for run_dir in sorted((ROOT / "results").iterdir()):
        if run_dir.name == "key":
            continue
        got = answers(run_dir.name)
        shared = [c for c in got if key.get(c) in ("yes", "no")]
        agree = sum(got[c] == key[c] for c in shared)
        missed = sum(key[c] == "yes" and got[c] == "no" for c in shared)
        extra = sum(key[c] == "no" and got[c] == "yes" for c in shared)
        unparsed = sum(got[c] == "unparsed" for c in shared)
        cost = sum(json.loads(p.read_text())["cost_usd"] or 0 for p in run_dir.glob("*.json"))
        print(
            f"{run_dir.name:8} {agree:3}/{len(shared):<3} {missed:7}  {extra:7}  {unparsed:8}  ${cost:.2f}"
        )


if __name__ == "__main__":
    main()
