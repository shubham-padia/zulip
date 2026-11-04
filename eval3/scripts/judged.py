"""Share of top-1 misses that the judge found reasonable, per variant and run."""
import json
from common import *
S = json.load(open(P('eval3', 'scores.json')))
J = {}
for key in S['misses']:
    pr, login = key.split()
    J[key] = json.loads(open(P('eval3', 'judge', f'{pr}_{login}.json')).read().strip())
out = {}
for v in VARIANTS:
    for r in RUNS:
        k = f'{v}/run{r}'
        m = [key for key, runs in S['misses'].items() if k in runs]
        ok = sum(J[key]['reasonable'] for key in m)
        out[k] = (ok, len(m))
        print(k, f'{ok}/{len(m)} misses reasonable')
print('unique pairs reasonable:', sum(j['reasonable'] for j in J.values()), '/', len(J))
json.dump({'per_run': out, 'verdicts': J}, open(P('eval3', 'judged.json'), 'w'), indent=1)
