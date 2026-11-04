import json, re, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def P(*a): return os.path.join(ROOT, *a)
CASES = json.load(open(P('cases.json')))
HIST = json.load(open(P('handoff_history.json')))
MAINT = [l.strip() for l in open(P('maintainers.txt')) if l.strip()]
NAME2LOGIN = {}
for line in open(P('maintainer_names.tsv')):
    login, _, name = line.rstrip('\n').partition('\t')
    if name and not name.startswith(('{', '"', '}')):
        NAME2LOGIN[name] = login
# Logins whose display name is missing from maintainer_names.tsv, or whose
# git author name differs from it.
NAME2LOGIN.update({'Pratik Chanda': 'pratik-pc', 'Prakhar Pratyush': 'prakhar1144',
                   'Emily Sutherlin': 'emilysutherlin', 'PieterCK': 'PieterCK'})
VARIANTS = ['v1_file_history', 'v2_area_activity']
RUNS = [1, 2]
def meta(pr): return json.load(open(P('inputs', f'{pr}.meta.json')))
def parse_output(text):
    logins = []
    for m in re.finditer(r'^\s*\d+\.\s*@([A-Za-z0-9-]+)', text, re.M):
        if m.group(1) not in logins: logins.append(m.group(1))
    return logins[:3]
def out_path(v, r, pr): return P('eval3', 'runs', v, f'run{r}', f'{pr}.md')
