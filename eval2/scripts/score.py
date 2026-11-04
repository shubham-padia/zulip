#!/usr/bin/env python3
"""Summarize eval 2 into eval2/results/summary.json and print a text summary.

Decision accuracy compares each output's first line (NOTHING/NOTE/CARD)
with the key's decision. Action accuracy compares the action the judge
read from the output with the key's triager_action. Judge scores are
averaged over the two judge repeats; the spread is reported as each
repeat's mean, and as the mean of the two bot runs separately.
overall = mean of the four scores (brevity is null for NOTHING outputs and
is then left out).
"""

import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent
VARIANTS = ("v1", "v2", "v3")
REPEATS = (1, 2)
PARTS = ("decision_score", "accuracy_score", "reply_score", "brevity_score")


def load(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def overall(scores: dict) -> float:
    values = [scores[p] for p in PARTS if scores.get(p) is not None]
    return sum(values) / len(values)


def mean(values: list[float]) -> float | None:
    return round(statistics.mean(values), 2) if values else None


def mean_se(values: list[float]) -> str:
    if len(values) < 2:
        return "n/a"
    se = statistics.stdev(values) / math.sqrt(len(values))
    return f"{statistics.mean(values):+.2f} ± {se:.2f}"


cases = json.loads((EVAL / "cases.json").read_text())
keys = {c["id"]: load(EVAL / f"keys/{c['id']}.json") for c in cases}
# per (variant, repeat, case): {"kind", "scores": {judge repeat: {...}}}
rows: dict[tuple[str, int, str], dict] = {}
for case in cases:
    cid = case["id"]
    for variant in VARIANTS:
        for repeat in REPEATS:
            out = load(EVAL / f"outputs/{variant}-r{repeat}/{cid}.json")
            if out:
                rows[(variant, repeat, cid)] = {"kind": out["kind"], "text": out["text"], "scores": {}}
    for judge_repeat in (1, 2):
        judged = load(EVAL / f"judgments/j{judge_repeat}/{cid}.json")
        if not judged:
            continue
        for letter, runs in judged["map"].items():
            scores = judged["judgment"]["outputs"][letter]
            for run in runs:
                variant, repeat = run.split("-r")
                rows[(variant, int(repeat), cid)]["scores"][judge_repeat] = scores

judged_cases = sorted({cid for (_, _, cid), row in rows.items() if len(row["scores"]) == 2})
summary: dict = {"cases_total": len(cases), "cases_with_keys": sum(1 for k in keys.values() if k),
                 "cases_judged_twice": len(judged_cases), "variants": {}}
key_decisions = Counter(k["key"]["decision"] for k in keys.values() if k)
key_actions = Counter(k["key"]["triager_action"] for k in keys.values() if k)
summary["key_decisions"], summary["key_actions"] = dict(key_decisions), dict(key_actions)
groups = {c["id"]: c["group"] for c in cases}

per_case_overall: dict[str, dict[str, float]] = defaultdict(dict)
for variant in VARIANTS:
    info: dict = {}
    kinds_right, kinds_total, actions_right, actions_total = [], 0, [], 0
    confusion: Counter = Counter()
    by_group: dict[str, list[int]] = defaultdict(list)
    part_values: dict[str, list[float]] = defaultdict(list)
    per_judge: dict[int, list[float]] = defaultdict(list)
    per_run: dict[int, list[float]] = defaultdict(list)
    wrong_facts, rule_failures = [], Counter()
    for (v, repeat, cid), row in rows.items():
        if v != variant or not keys.get(cid):
            continue
        key = keys[cid]["key"]
        right = int(row["kind"] == key["decision"])
        kinds_right.append(right)
        confusion[f"key {key['decision']} -> {row['kind']}"] += 1
        by_group[groups[cid]].append(right)
        if cid not in judged_cases:
            continue
        case_overalls = []
        for judge_repeat, scores in row["scores"].items():
            actions_right.append(int(scores.get("action") == key["triager_action"]))
            for part in PARTS:
                if scores.get(part) is not None:
                    part_values[part].append(scores[part])
            o = overall(scores)
            per_judge[judge_repeat].append(o)
            per_run[repeat].append(o)
            case_overalls.append(o)
            wrong_facts.append(len(scores.get("wrong_facts") or []))
            rule_failures.update(scores.get("rule_failures") or [])
        row["overall"] = statistics.mean(case_overalls)
        per_case_overall[cid].setdefault(variant, 0.0)
        per_case_overall[cid][variant] += row["overall"] / len(REPEATS)
    info["decision_accuracy"] = mean(kinds_right)
    info["decision_accuracy_by_group"] = {g: mean(v) for g, v in sorted(by_group.items())}
    info["decision_confusion"] = dict(sorted(confusion.items()))
    info["action_accuracy"] = mean(actions_right)
    info["scores"] = {p: mean(v) for p, v in part_values.items()}
    info["overall"] = mean(per_judge[1] + per_judge[2])
    info["overall_judge_repeat_1"] = mean(per_judge[1])
    info["overall_judge_repeat_2"] = mean(per_judge[2])
    info["overall_bot_run_1"] = mean(per_run[1])
    info["overall_bot_run_2"] = mean(per_run[2])
    info["wrong_facts_per_output"] = mean(wrong_facts)
    info["top_rule_failures"] = rule_failures.most_common(6)
    summary["variants"][variant] = info

pairs = {}
for a, b in (("v1", "v2"), ("v1", "v3"), ("v2", "v3")):
    diffs = [per_case_overall[c][a] - per_case_overall[c][b] for c in judged_cases
             if a in per_case_overall[c] and b in per_case_overall[c]]
    pairs[f"{a} - {b}"] = mean_se(diffs)
summary["paired_overall_differences"] = pairs

ranked = sorted(
    ((row["overall"], v, r, cid, row["kind"]) for (v, r, cid), row in rows.items() if "overall" in row),
)
summary["outputs_ranked"] = [
    {"variant": v, "repeat": r, "case": cid, "kind": kind, "overall": round(o, 2)}
    for o, v, r, cid, kind in ranked
]
out = EVAL / "results/summary.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary, indent=1))
printable = {k: v for k, v in summary.items() if k != "outputs_ranked"}
print(json.dumps(printable, indent=1))
