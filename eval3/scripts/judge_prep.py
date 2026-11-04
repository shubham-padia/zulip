"""Write one judge-context file per unjudged top-1 miss (PR, suggested login)."""
import json, os, collections
from common import *
S = json.load(open(P('eval3', 'scores.json')))
out_dir = os.environ['JUDGE_CTX_DIR']
os.makedirs(out_dir, exist_ok=True)
todo = []
for key, runs in sorted(S['misses'].items()):
    pr, login = key.split()
    pr = int(pr)
    if os.path.exists(P('eval3', 'judge', f'{pr}_{login}.json')):
        continue
    c = next(c for c in CASES if c['pr'] == pr)
    files = set(meta(pr)['files'])
    tops = {f.split('/')[0] for f in files}
    dirs = {f.rsplit('/', 1)[0] for f in files}
    shared, near = [], collections.Counter()
    for h in HIST:
        if h['pr'] == pr or h['assigned_at'] >= c['cutoff']: continue
        hf = set(h['files'] or [])
        if hf & files:
            shared.append(f"- #{h['pr']} ({h['assigned_at'][:10]}): assignee {h['assignee']}; shared files: {', '.join(sorted(hf & files)[:4])}")
        if {f.rsplit('/', 1)[0] for f in hf} & dirs:
            near[h['assignee']] += 1
    reasons = []
    for vr in runs:
        v, r = vr.split('/')
        text = open(out_path(v, int(r[3:]), pr)).read().strip().splitlines()[0]
        reasons.append(f"- {vr}: {text}")
    ctx = f"""# Judge context for PR #{pr}
Suggested top-1 reviewer: @{login}
Reviewer the triager actually assigned: @{c['assignee']}
PR author: {c['author']}
Hand-off time: {c['cutoff']}

## Bot's top line(s) that suggested @{login}
{chr(10).join(reasons)}

## Earlier hand-offs (before this one) that touched the same files
{chr(10).join(shared[-15:]) or '(none)'}

## Assignees of earlier hand-offs touching the same directories (count)
{', '.join(f'{k}: {v}' for k, v in near.most_common(8)) or '(none)'}
"""
    open(os.path.join(out_dir, f'{pr}_{login}.md'), 'w').write(ctx)
    todo.append(f'{pr}_{login}')
print(len(todo)); print(' '.join(todo))
