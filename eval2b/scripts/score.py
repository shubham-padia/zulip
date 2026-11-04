#!/usr/bin/env python3
"""Score eval 2b into eval2b/results/<name>.json and print a summary.

  score.py tune <variant>      the revision vs the eval 2 v3-r1 baseline,
                               judged side by side once per tune case
  score.py heldout <variant>   <variant> vs v3, 2 bot runs x 2 judge repeats

Same measures as eval2/scripts/score.py: action accuracy (judge's reading
of the output vs the key's triager_action), decision accuracy, the four
scores, overall = mean of the four, wrong facts, words per output. Spread
is given per bot run and per judge repeat; paired differences are per case
(mean ± SE).
"""

import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
EVAL2 = HERE.parent / "eval2"
PARTS = ("decision_score", "accuracy_score", "reply_score", "brevity_score")
SPLIT = json.loads((HERE / "split.json").read_text())


def overall(s: dict) -> float:
    vals = [s[p] for p in PARTS if s.get(p) is not None]
    return sum(vals) / len(vals)


def m(vals):
    return round(statistics.mean(vals), 3) if vals else None


def mean_se(vals):
    if len(vals) < 2:
        return None
    return {"mean": round(statistics.mean(vals), 3),
            "se": round(statistics.stdev(vals) / math.sqrt(len(vals)), 3), "n": len(vals)}


def output_text(run: str, cid: str) -> str:
    path = (EVAL2 / f"outputs/{run[6:]}/{cid}.json" if run.startswith("eval2:")
            else HERE / f"outputs/{run}/{cid}.json")
    return json.loads(path.read_text())["text"]


def main() -> None:
    mode, variant = sys.argv[1], sys.argv[2]
    name = f"{mode}-{variant}"
    cases = [c for c in SPLIT["tune" if mode == "tune" else "heldout"] if c not in SPLIT["excluded"]]
    keys = {c: json.loads((EVAL2 / f"keys/{c}.json").read_text())["key"] for c in cases}
    # rows[(label, bot_run, cid, judge_repeat)] = scores
    rows = {}
    texts = {}
    for cid in cases:
        for jr in (1, 2):
            p = HERE / f"judgments/{name}/j{jr}/{cid}.json"
            if not p.exists():
                continue
            j = json.loads(p.read_text())
            for letter, runs in j["map"].items():
                for run in runs:
                    label, r = run.split(":")[-1].split("-r")
                    label = "v3" if label == "v3" else label
                    rows[(label, int(r), cid, jr)] = j["judgment"]["outputs"][letter]
                    texts[(label, int(r), cid)] = output_text(run, cid)
    labels = sorted({k[0] for k in rows})
    result = {"cases": len(cases), "variants": {}}
    per_case = defaultdict(dict)
    for label in labels:
        mine = {k: v for k, v in rows.items() if k[0] == label}
        acts = [int(s.get("action") == keys[k[2]]["triager_action"]) for k, s in mine.items()]
        kinds = [int(s.get("kind") == keys[k[2]]["decision"]) for k, s in mine.items()]
        parts = {p: m([s[p] for s in mine.values() if s.get(p) is not None]) for p in PARTS}
        by_run, by_judge = defaultdict(list), defaultdict(list)
        act_by_run = defaultdict(list)
        case_vals = defaultdict(list)
        confusion = Counter()
        failures = Counter()
        for (lab, r, cid, jr), s in mine.items():
            o = overall(s)
            by_run[r].append(o)
            by_judge[jr].append(o)
            act_by_run[r].append(int(s.get("action") == keys[cid]["triager_action"]))
            case_vals[cid].append(o)
            confusion[f"{keys[cid]['triager_action']} -> {s.get('action')}"] += 1
            failures.update(s.get("rule_failures") or [])
        for cid, vals in case_vals.items():
            per_case[cid][label] = statistics.mean(vals)
        words = [len(t.split()) for (lab, r, cid), t in texts.items() if lab == label]
        result["variants"][label] = {
            "n_scored": len(mine),
            "action_accuracy": m(acts),
            "action_accuracy_by_bot_run": {r: m(v) for r, v in sorted(act_by_run.items())},
            "decision_accuracy": m(kinds),
            "scores": parts,
            "overall": m([overall(s) for s in mine.values()]),
            "overall_by_bot_run": {r: m(v) for r, v in sorted(by_run.items())},
            "overall_by_judge_repeat": {r: m(v) for r, v in sorted(by_judge.items())},
            "wrong_facts_per_output": m([len(s.get("wrong_facts") or []) for s in mine.values()]),
            "words_per_output": m(words),
            "action_confusion": dict(sorted(confusion.items())),
            "top_rule_failures": failures.most_common(6),
        }
    other = [lab for lab in labels if lab != "v3"]
    if other and "v3" in labels:
        new = other[0]
        diffs = [per_case[c][new] - per_case[c]["v3"] for c in cases if new in per_case[c] and "v3" in per_case[c]]
        result[f"paired_overall_{new}_minus_v3"] = mean_se(diffs)
        adiff = []
        for c in cases:
            a = [int(s.get("action") == keys[c]["triager_action"]) for k, s in rows.items() if k[2] == c and k[0] == new]
            b = [int(s.get("action") == keys[c]["triager_action"]) for k, s in rows.items() if k[2] == c and k[0] == "v3"]
            if a and b:
                adiff.append(statistics.mean(a) - statistics.mean(b))
        result[f"paired_action_{new}_minus_v3"] = mean_se(adiff)
        result["per_case"] = {
            c: {"key": keys[c]["triager_action"],
                **{lab: [rows[k].get("action") for k in sorted(rows) if k[2] == c and k[0] == lab] for lab in labels},
                **{f"overall_{lab}": round(per_case[c].get(lab, float("nan")), 2) for lab in labels}}
            for c in cases}
    out = HERE / f"results/{name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k != "per_case"}, indent=1))


if __name__ == "__main__":
    main()
