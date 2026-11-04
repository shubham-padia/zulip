#!/bin/bash
cd /home/zulipdev/zulip/.claude/worktrees/agent-a1c9249fe4d0d2733
for p in /home/zulipdev/zulip/wt-triage-eval3/part_*; do
  timeout 2h xargs -a "$p" uv run -q --frozen --only-group release-tools python /home/zulipdev/zulip/wt-triage-eval3/gather3.py >> /home/zulipdev/zulip/wt-triage-eval3/gather.log 2>&1 &
done
wait
cd /home/zulipdev/zulip/wt-triage-eval3
python3 -I -c 'import json; print("\n".join(sorted({str(h["pr"]) for h in json.load(open("handoff_history.json"))})))' | xargs -P 6 -I{} sh -c '[ -s cache/files_{}.json ] || gh api -X GET "repos/zulip/zulip/pulls/{}/files?per_page=100" --paginate --jq "[.[].filename]" > cache/files_{}.json 2>/dev/null'
for m in $(cat maintainers.txt); do printf "%s\t%s\n" "$m" "$(gh api users/$m --jq .name 2>/dev/null)"; done > maintainer_names.tsv
echo ALLDONE >> gather.log
