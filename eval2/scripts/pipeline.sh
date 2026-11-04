#!/bin/bash
# Run the key and bot stages on gathered cases while gathering goes on,
# then judge. Each pass only does missing work. Ends after the judge
# stage, or after 6 hours.
set -u
cd "$(dirname "$0")/.."
end=$((SECONDS + 6 * 3600))
while [ "$SECONDS" -lt "$end" ]; do
    gathering=$(pgrep -f "scripts/gather_case.py" > /dev/null && echo yes || echo no)
    python3 scripts/run.py key || exit 1
    python3 scripts/run.py bot || exit 1
    if [ "$gathering" = no ]; then
        python3 scripts/run.py key || exit 1
        python3 scripts/run.py bot || exit 1
        python3 scripts/run.py judge || exit 1
        echo "pipeline done"
        exit 0
    fi
    sleep 300
done
echo "pipeline hit its time limit"
