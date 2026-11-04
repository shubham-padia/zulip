"""Extra breakdowns for the report: explicit review pings, run agreement."""
import json, re
from common import *
S = json.load(open(P('eval3', 'scores.json')))
D = S['detail']
ping = {}
for c in CASES:
    t = open(P('inputs', f"{c['pr']}.md")).read()
    # A maintainer comment that @-mentions the eventual assignee.
    ping[c['pr']] = any(
        re.match(r'- \[(\S+), maintainer', line) and '@' + c['assignee'] in line
        for line in t.splitlines())
easy = [p for p in ping if ping[p]]
print('cases where a maintainer comment @-mentions the eventual assignee:', len(easy))
for v in VARIANTS:
    for r in RUNS:
        k = f'{v}/run{r}'
        e = sum(D[str(p)][k][:1] == [D[str(p)]['assignee']] for p in easy)
        h = [p for p in ping if not ping[p]]
        o = sum(D[str(p)][k][:1] == [D[str(p)]['assignee']] for p in h)
        print(k, f'top1 on pinged {e}/{len(easy)}, on others {o}/{len(h)}')
    same = sum(D[str(c['pr'])][f'{v}/run1'][:1] == D[str(c['pr'])][f'{v}/run2'][:1] for c in CASES)
    print(v, 'same top-1 in both runs:', same)
print('assignee not in maintainers.txt:', [c['pr'] for c in CASES if c['assignee'] not in MAINT])
json.dump({'pinged': easy}, open(P('eval3', 'analysis.json'), 'w'), indent=1)
