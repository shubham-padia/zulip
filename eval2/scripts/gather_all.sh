#!/bin/bash
# Gather every case in eval2/cases.json with 3 parallel workers.
# GitHub searches are spaced through a shared lock file. Existing outputs
# are skipped. With "rev", the workers go through the cases in reverse
# order, so a second run started alongside the first meets it in the
# middle.
set -u
cd "$(dirname "$0")/.."
mkdir -p logs
order=${1:-fwd}
python3 -c 'import json; print("\n".join(c["id"] for c in json.load(open("cases.json"))))' > "logs/case_ids_$order.txt"
if [ "$order" = rev ]; then
    tac "logs/case_ids_$order.txt" > "logs/case_ids_$order.tmp"
    mv "logs/case_ids_$order.tmp" "logs/case_ids_$order.txt"
fi
split -n r/3 "logs/case_ids_$order.txt" "logs/ids_${order}_"
for part in logs/ids_"${order}"_*; do
    timeout 3h xargs -a "$part" python3 scripts/gather_case.py >> "logs/gather_$order.log" 2>&1 &
done
wait
rm -f logs/ids_"${order}"_*
echo "gather done"
