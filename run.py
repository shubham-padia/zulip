#!/usr/bin/env python3
"""Run eval 1: does an author's comment on a "not ready" PR ask for
another look?

Stage "key": Opus labels every case once (the answer key).
Stage "bot": Sonnet answers every case with prompts v1-v3, twice each.

Every call is one `claude -p` with a replaced system prompt and no
tools.  Each result is saved to results/<run>/<case>.json, and cases
that already have a result are skipped, so a rerun only does missing
work.  Results are committed and pushed every PUSH_EVERY calls.

Usage: ./run.py key   then   ./run.py bot
"""

import json
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_CHARS = 6000
WORKERS = 4
PUSH_EVERY = 20
PUSH_REMOTE = "git@github.com:shubham-padia/zulip.git"
PUSH_BRANCH = "triage-eval1"

STAGES = {
    "key": [("key", "opus", "high", "key")],
    "bot": [
        (f"{variant}-r{repeat}", "sonnet", None, variant)
        for variant in ("v1", "v2", "v3")
        for repeat in (1, 2)
    ],
}

lock = threading.Lock()
done_since_push = 0


def clip(text: str) -> str:
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS] + "\n[…cut]"


def case_input(case: dict) -> str:
    parts = [f"PR #{case['pr']}"]
    previous = case["previous_maintainer_comment"]
    if previous:
        parts.append(
            f"Maintainer comment before the author's (by {previous['author']}):\n"
            f"<maintainer_comment>\n{clip(previous['body'])}\n</maintainer_comment>"
        )
    else:
        parts.append("There is no maintainer comment before the author's.")
    parts.append(
        f"The author's comment (by {case['author']}):\n"
        f"<author_comment>\n{clip(case['author_comment']['body'])}\n</author_comment>"
    )
    return "\n\n".join(parts)


def push(message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        return
    subprocess.run(["git", "commit", "-qm", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "-q", "-f", PUSH_REMOTE, f"HEAD:{PUSH_BRANCH}"], cwd=ROOT)


def run_one(run: str, model: str, effort: str | None, prompt: str, case: dict) -> None:
    global done_since_push
    out = ROOT / "results" / run / f"{case['id']}.json"
    if out.exists():
        return
    command = [
        "claude", "-p", "--model", model,
        "--system-prompt", (ROOT / "prompts" / f"{prompt}.md").read_text(),
        "--tools", "", "--setting-sources", "", "--strict-mcp-config",
        "--no-session-persistence", "--output-format", "json",
    ]
    if effort:
        command += ["--effort", effort]
    result = subprocess.run(
        command, input=case_input(case), capture_output=True, text=True, timeout=600
    )
    if result.returncode != 0:
        print(f"FAILED {run} {case['id']}: {result.stderr.strip()[:300]}", flush=True)
        return
    data = json.loads(result.stdout)
    answer = data.get("result", "").strip()
    first = answer.splitlines()[0].strip().lower().strip(".*") if answer else ""
    record = {
        "case": case["id"],
        "answer": first if first in ("yes", "no") else "unparsed",
        "text": answer,
        "cost_usd": data.get("total_cost_usd"),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1))
    with lock:
        done_since_push += 1
        if done_since_push >= PUSH_EVERY:
            done_since_push = 0
            push(f"Results up to {run} {case['id']}.")


def main() -> None:
    stage = sys.argv[1]
    cases = json.loads((ROOT / "cases.json").read_text())
    jobs = [
        (run, model, effort, prompt, case)
        for run, model, effort, prompt in STAGES[stage]
        for case in cases
    ]
    with ThreadPoolExecutor(WORKERS) as pool:
        for future in [pool.submit(run_one, *job) for job in jobs]:
            future.result()
    push(f"Stage {stage} done.")


if __name__ == "__main__":
    main()
