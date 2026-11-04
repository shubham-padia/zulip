"""Score bot runs and baselines; list top-1 misses that still need judging."""
import json, os, statistics
from common import *
base = json.load(open(P('eval3', 'baselines.json')))
truth = {c['pr']: c for c in CASES}
rows = {}
misses = {}  # (pr, login) -> list of (variant, run)
detail = {}
for v in VARIANTS:
    for r in RUNS:
        t1 = t3 = n = invalid = author_sugg = 0
        for pr, c in truth.items():
            f = out_path(v, r, pr)
            if not os.path.exists(f): continue
            n += 1
            sugg = parse_output(open(f).read())
            invalid += any(l not in MAINT for l in sugg)
            author_sugg += c['author'] in sugg
            detail.setdefault(pr, {})[f'{v}/run{r}'] = sugg
            if sugg[:1] == [c['assignee']]: t1 += 1
            elif sugg: misses.setdefault(f'{pr} {sugg[0]}', []).append(f'{v}/run{r}')
            if c['assignee'] in sugg: t3 += 1
        rows[f'{v}/run{r}'] = dict(n=n, top1=t1, top3=t3, invalid=invalid, author=author_sugg)
for k in ['a_file_author', 'b_path_history']:
    rows[k] = dict(n=len(CASES), top1=sum(base[str(p)][k][:1] == [c['assignee']] for p, c in truth.items()),
                   top3=sum(c['assignee'] in base[str(p)][k] for p, c in truth.items()))
for pr, c in truth.items():
    detail.setdefault(pr, {})['assignee'] = c['assignee']
json.dump({'rows': rows, 'misses': misses, 'detail': detail}, open(P('eval3', 'scores.json'), 'w'), indent=1)
for k, v in rows.items(): print(k, v)
print('unique top-1 misses:', len(misses))
