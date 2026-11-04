#!/usr/bin/env python3
"""Split the 60 eval 2 cases into a tune set and a held-out set (30 each).

Stratified by `group` with a fixed seed: within each group the cases are
shuffled and dealt alternately, starting with whichever set is smaller so
far. Case 39863-5344084962 stays in the split but is never run or scored,
because its key is known to be wrong.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

EVAL2 = Path(__file__).resolve().parent.parent.parent / "eval2"
OUT = Path(__file__).resolve().parent.parent / "split.json"
SEED = 20261104
EXCLUDED = ["39863-5344084962"]

cases = json.loads((EVAL2 / "cases.json").read_text())
by_group = defaultdict(list)
for case in cases:
    by_group[case["group"]].append(case["id"])
rng = random.Random(SEED)
sets = {"tune": [], "heldout": []}
for group in sorted(by_group):
    ids = sorted(by_group[group])
    rng.shuffle(ids)
    first = "tune" if len(sets["tune"]) <= len(sets["heldout"]) else "heldout"
    second = "heldout" if first == "tune" else "tune"
    for i, cid in enumerate(ids):
        sets[first if i % 2 == 0 else second].append(cid)
OUT.write_text(json.dumps({"seed": SEED, "excluded": EXCLUDED,
                           "tune": sorted(sets["tune"]), "heldout": sorted(sets["heldout"])}, indent=1))
groups = {c["id"]: c["group"] for c in cases}
for name, ids in sets.items():
    counts = defaultdict(int)
    for cid in ids:
        counts[groups[cid]] += 1
    print(name, len(ids), dict(counts), "excluded here:", [c for c in EXCLUDED if c in ids])
