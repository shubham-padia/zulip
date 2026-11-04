"""Score eval2c: v3f vs v3 facts, from judgments/j<n>/*.json and judge_maps."""
import json, re, statistics as st
from pathlib import Path

root = Path(__file__).resolve().parents[2]
EXCLUDE = {"39863-5344084962"}
RUNS = ["v3f-r1", "v3f-r2", "v3-r1", "v3-r2"]
cases = [c["id"] for c in json.loads((root / "eval2/cases.json").read_text())]

def text(run, case):
    if run.startswith("v3f"):
        return (root / f"eval2c/outputs/{run}/{case}.md").read_text().strip()
    return json.loads((root / f"eval2/outputs/{run}/{case}.json").read_text())["text"].strip()

def facts_words(run, t):
    """Words in the New/Missing part only (v3 also has a verdict, next step and reply)."""
    if run.startswith("v3f"):
        return len(t.split())
    m = re.search(r"New:.*?(?=\n#|\Z)", t, re.S)
    return len(m.group(0).split()) if m else 0

rows = []
for case in cases:
    for j in (1, 2):
        d = json.loads(re.search(r"\{.*\}", (root / f"eval2c/judgments/j{j}/{case}.json").read_text(), re.S).group(0))
        m = json.loads((root / f"eval2c/judge_maps/j{j}/{case}.json").read_text())
        for letter, run in m.items():
            o = d["outputs"][letter]
            t = text(run, case)
            rows.append(dict(case=case, judge=j, run=run, variant=run.split("-")[0],
                             score=float(o["facts_score"]), wrong=len(o["wrong_facts"]),
                             missed=len(o["missed"]), why=o.get("why", ""),
                             words=len(t.split()), fwords=facts_words(run, t),
                             kind=t.splitlines()[0].strip("*` ").upper()))

scored = [r for r in rows if r["case"] not in EXCLUDE]
def mean(xs): return sum(xs) / len(xs)
out = {}
for v in ("v3f", "v3"):
    rs = [r for r in scored if r["variant"] == v]
    out[v] = dict(
        n=len(rs), score=mean([r["score"] for r in rs]),
        by_run={run: mean([r["score"] for r in rs if r["run"] == run]) for run in RUNS if run.startswith(v + "-")},
        by_judge={j: mean([r["score"] for r in rs if r["judge"] == j]) for j in (1, 2)},
        wrong=mean([r["wrong"] for r in rs]), missed=mean([r["missed"] for r in rs]),
        words=mean([r["words"] for r in rs if r["judge"] == 1]),
        fwords=mean([r["fwords"] for r in rs if r["judge"] == 1]),
        low=sum(r["score"] <= 4 for r in rs) / len(rs),
    )
diffs = []
for case in sorted({r["case"] for r in scored}):
    a = mean([r["score"] for r in scored if r["case"] == case and r["variant"] == "v3f"])
    b = mean([r["score"] for r in scored if r["case"] == case and r["variant"] == "v3"])
    diffs.append((a - b, case))
d = [x for x, _ in diffs]
out["paired"] = dict(mean=mean(d), se=st.stdev(d) / len(d) ** 0.5, n=len(d),
                     v3f_better=sum(x > 0 for x in d), v3_better=sum(x < 0 for x in d), tie=sum(x == 0 for x in d),
                     worst=sorted(diffs)[:5], best=sorted(diffs)[-5:])
judge_agree = mean([abs(a["score"] - b["score"]) for a in rows if a["judge"] == 1
                    for b in rows if b["judge"] == 2 and b["case"] == a["case"] and b["run"] == a["run"]])
out["judge_repeat_mean_abs_diff"] = judge_agree
kinds = {}
for r in rows:
    if r["variant"] == "v3f" and r["judge"] == 1:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
out["v3f_kinds_all60x2"] = kinds
per_output = {}
for r in scored:
    if r["variant"] == "v3f":
        per_output.setdefault((r["case"], r["run"]), []).append(r)
ranked = sorted(((mean([x["score"] for x in v]), k, [x["why"] for x in v]) for k, v in per_output.items()))
out["v3f_ranked"] = [dict(score=s, case=k[0], run=k[1], why=w) for s, k, w in ranked]
(root / "eval2c/results").mkdir(exist_ok=True)
(root / "eval2c/results/summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "v3f_ranked"}, indent=1))
