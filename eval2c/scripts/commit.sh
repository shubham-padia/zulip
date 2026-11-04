#!/bin/bash
# Commit eval2c/ and push to the run branch.
cd "$(dirname "$0")/../.." || exit 1
git add eval2c
git commit -q -m "eval2c: $1" && for i in 1 2 3 4; do git push -q -f -u origin triage-eval2c-run && break; sleep $((2**i)); done
