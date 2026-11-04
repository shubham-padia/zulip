#!/bin/bash
# Gather every case in eval2/cases.json with 3 parallel workers.
# GitHub searches are spaced through a shared lock file, so more workers
# don't help much. Existing outputs are skipped.
set -u
cd "$(dirname "$0")/.."
mkdir -p logs
python3 -c 'import json; print("\n".join(c["id"] for c in json.load(open("cases.json"))))' > logs/case_ids.txt
split -n r/3 logs/case_ids.txt logs/ids_part_
for part in logs/ids_part_*; do
    timeout 3h xargs -a "$part" python3 scripts/gather_case.py >> logs/gather.log 2>&1 &
done
wait
rm -f logs/ids_part_*
echo "gather done"
