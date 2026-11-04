"""Build blind judge inputs: one scratch folder per (case, judge repeat).

Each folder gets cutoff.md, all.md, key.json and outputs.md, where outputs.md
holds v3f-r1, v3f-r2, v3-r1 and v3-r2 under fresh random letters in a random
order. The letter map is saved to eval2c/judge_maps/j<n>/<case>.json.
"""
import json, random, shutil, string, sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
scratch = Path(sys.argv[1])
RUNS = ["v3f-r1", "v3f-r2", "v3-r1", "v3-r2"]

def text(run, case):
    if run.startswith("v3f"):
        p = root / f"eval2c/outputs/{run}/{case}.md"
        return p.read_text().strip() if p.exists() else None
    return json.loads((root / f"eval2/outputs/{run}/{case}.json").read_text())["text"].strip()

for c in json.loads((root / "eval2/cases.json").read_text()):
    case = c["id"]
    texts = {r: text(r, case) for r in RUNS}
    if None in texts.values():
        print("missing outputs", case); continue
    for j in (1, 2):
        rng = random.Random(f"eval2c-{case}-j{j}")
        letters = rng.sample(string.ascii_uppercase, len(RUNS))
        order = RUNS[:]; rng.shuffle(order)
        mapping = dict(zip(letters, order))
        mp = root / f"eval2c/judge_maps/j{j}/{case}.json"
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(mapping, indent=1) + "\n")
        d = scratch / "judge" / f"{case}-j{j}"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(root / f"eval2/inputs/{case}.cutoff.md", d / "cutoff.md")
        shutil.copy(root / f"eval2/inputs/{case}.all.md", d / "all.md")
        key = json.loads((root / f"eval2/keys/{case}.json").read_text())["key"]
        (d / "key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False))
        (d / "outputs.md").write_text("\n\n".join(f"=== OUTPUT {l} ===\n{texts[r]}" for l, r in mapping.items()) + "\n")
