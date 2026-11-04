"""List judgments that are missing, unparsable, or don't cover every letter."""
import json, re
from pathlib import Path
root = Path(__file__).resolve().parents[2]
bad, ok = [], 0
for c in json.loads((root / "eval2/cases.json").read_text()):
    for j in (1, 2):
        p = root / f"eval2c/judgments/j{j}/{c['id']}.json"
        if not p.exists():
            bad.append(f"missing j{j} {c['id']}"); continue
        m = json.loads((root / f"eval2c/judge_maps/j{j}/{c['id']}.json").read_text())
        try:
            t = p.read_text(); d = json.loads(re.search(r"\{.*\}", t, re.S).group(0))
            assert set(d["outputs"]) == set(m)
            for v in d["outputs"].values(): int(v["facts_score"])
            ok += 1
        except Exception as e:
            bad.append(f"bad j{j} {c['id']}: {e!r}")
print(ok, "ok"); print("\n".join(b for b in bad if not b.startswith("missing")))
print(sum(b.startswith("missing") for b in bad), "missing")
