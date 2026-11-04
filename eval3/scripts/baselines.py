import json, collections
from common import *
res = {}
for c in CASES:
    pr, author, cut = c['pr'], c['author'], c['cutoff']
    a = None
    for name, _n in meta(pr)['file_authors']:
        l = NAME2LOGIN.get(name)
        if l in MAINT and l != author:
            a = l; break
    tops = {f.split('/')[0] for f in meta(pr)['files']}
    cnt = collections.Counter(); last = {}
    for h in HIST:
        if h['pr'] == pr or h['assigned_at'] >= cut: continue
        if tops & {f.split('/')[0] for f in (h['files'] or [])} and h['assignee'] != author:
            cnt[h['assignee']] += 1; last[h['assignee']] = max(last.get(h['assignee'], ''), h['assigned_at'])
    # Most hand-offs first; ties go to the most recently assigned.
    ranked = sorted(sorted(cnt, key=lambda l: last[l], reverse=True), key=lambda l: -cnt[l])
    res[pr] = {'a_file_author': [a] if a else [], 'b_path_history': ranked[:3],
               'b_counts': {l: cnt[l] for l in ranked[:5]}}
json.dump(res, open(P('eval3', 'baselines.json'), 'w'), indent=1)
