#!/usr/bin/env python3
"""Print one case's key, an output, and the judges' notes on it.

  show.py CASE VARIANT-rREPEAT
"""

import json
import sys
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent
case, run = sys.argv[1], sys.argv[2]
key = json.loads((EVAL / f"keys/{case}.json").read_text())["key"]
print("KEY:", key["decision"], key["triager_action"], key["action_source"], "|", key["action_why"])
print("still missing:", key["still_missing"])
print("reply_ask:", key["reply_ask"])
print("--- OUTPUT", run)
print(json.loads((EVAL / f"outputs/{run}/{case}.json").read_text())["text"])
for j in (1, 2):
    judged = json.loads((EVAL / f"judgments/j{j}/{case}.json").read_text())
    letter = next(letter for letter, runs in judged["map"].items() if run in runs)
    o = judged["judgment"]["outputs"][letter]
    print(f"--- judge {j}: {o['action']} d{o['decision_score']} a{o['accuracy_score']} "
          f"r{o['reply_score']} b{o['brevity_score']} wrong={o['wrong_facts']} rules={o['rule_failures']}")
    print("  ", o.get("decision_why"), "|", o.get("reply_why"))
