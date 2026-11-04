#!/usr/bin/env python3
"""Run eval 2: the second look at a "not ready" PR after an author comment.

  run.py key      Opus writes the answer key for every gathered case.
  run.py bot      Sonnet runs prompts v1-v3 on every case, twice each.
  run.py judge    Opus judges every case twice, with fresh letters/order.

Every call is one fresh `claude -p` with no tools, no settings, skills or
MCP servers, and no saved session. The prompt and input go in the call; it
is told to reply with the output only. Results are saved under eval2/, and
work that already has a result is skipped, so a rerun only does missing
work. Results are committed every COMMIT_EVERY calls and pushed (a failed
push is ignored).

Only Sonnet (bot) and Opus (key, judge) may run: the model gate checks the
model each call reports and stops the run on anything else. The run also
stops starting calls after DEADLINE.
"""

import json
import random
import re
import string
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EVAL = Path(__file__).resolve().parent.parent
ROOT = EVAL.parent
VARIANTS = ("v1", "v2", "v3")
REPEATS = (1, 2)
JUDGE_REPEATS = (1, 2)
ALLOWED_MODELS = {"sonnet": "claude-sonnet-", "opus": "claude-opus-"}
WORKERS = {"key": 4, "bot": 6, "judge": 4}
COMMIT_EVERY = 20
DEADLINE = time.time() + 5 * 3600
PUSH_REMOTE = "https://github.com/shubham-padia/zulip.git"
PUSH_BRANCH = "triage-eval2"
NO_TOOLS = (
    "Don't read files or use tools: everything you need is in this message. "
    "Reply with the output only."
)

TRAILER = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

lock = threading.Lock()
done_since_commit = 0
stop = threading.Event()


def commit(message: str) -> None:
    with lock:
        subprocess.run(["git", "add", "eval2"], cwd=ROOT, check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
            return
        subprocess.run(["git", "commit", "-qm", message + TRAILER], cwd=ROOT, check=True)
        result = subprocess.run(
            ["git", "-c", "credential.helper=!gh auth git-credential", "push", "-q", "-f",
             PUSH_REMOTE, f"HEAD:{PUSH_BRANCH}"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"push failed: {result.stderr.strip()[:200]}", flush=True)


def call(model: str, effort: str | None, system: str, user: str) -> dict | None:
    if stop.is_set() or time.time() > DEADLINE:
        stop.set()
        return None
    command = [
        "claude", "-p", "--model", model, "--system-prompt", system,
        "--tools", "", "--setting-sources", "", "--strict-mcp-config",
        "--no-session-persistence", "--output-format", "json",
    ]
    if effort:
        command += ["--effort", effort]
    for attempt in range(3):
        result = subprocess.run(
            command, input=user + "\n\n" + NO_TOOLS, capture_output=True, text=True,
            timeout=1200, cwd="/tmp",
        )
        if result.returncode == 0:
            break
        print(f"call failed (try {attempt + 1}): {result.stderr.strip()[:300]} {result.stdout[:300]}", flush=True)
        time.sleep(30)
    else:
        return None
    data = json.loads(result.stdout)
    used = list((data.get("modelUsage") or {}).keys())
    if not used or not all(name.startswith(ALLOWED_MODELS[model]) for name in used):
        print(f"MODEL GATE: asked for {model}, got {used}; stopping", flush=True)
        stop.set()
        return None
    return {"text": (data.get("result") or "").strip(), "models": used,
            "cost_usd": data.get("total_cost_usd")}


def save(path: Path, record: dict, label: str) -> None:
    global done_since_commit
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False))
    print(f"saved {path.relative_to(EVAL)}", flush=True)
    with lock:
        done_since_commit += 1
        due = done_since_commit >= COMMIT_EVERY
        if due:
            done_since_commit = 0
    if due:
        commit(f"eval2: Results up to {label}.")


def gathered_cases() -> list[dict]:
    cases = json.loads((EVAL / "cases.json").read_text())
    return [
        c for c in cases
        if (EVAL / f"inputs/{c['id']}.cutoff.md").exists()
        and (EVAL / f"inputs/{c['id']}.all.md").exists()
    ]


def fill(template: str, **values: str) -> str:
    for name, value in values.items():
        template = template.replace("{" + name + "}", value)
    return template


def what_happened(case: dict) -> str:
    extra = {
        "closed": " The PR was closed unmerged within those 14 days.",
        "removed": "",
        "replied": "",
        "no_action": "",
    }[case["group"]]
    return case["what_happened_next"] + "." + extra


def run_key(case: dict) -> None:
    out = EVAL / f"keys/{case['id']}.json"
    if out.exists():
        return
    prompt = fill(
        (EVAL / "prompts/key.md").read_text(),
        cutoff_facts=(EVAL / f"inputs/{case['id']}.cutoff.md").read_text(),
        all_facts=(EVAL / f"inputs/{case['id']}.all.md").read_text(),
        what_happened_next=what_happened(case),
    )
    result = call("opus", "high", "You prepare answer keys for an eval.", prompt)
    if result is None:
        return
    match = re.search(r"\{.*\}", result["text"], re.DOTALL)
    try:
        key = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        key = None
    if key is None:
        print(f"unparsed key for {case['id']}", flush=True)
        return
    save(out, {"case": case["id"], "key": key, **result}, f"key {case['id']}")


def run_bot(variant: str, repeat: int, case: dict) -> None:
    out = EVAL / f"outputs/{variant}-r{repeat}/{case['id']}.json"
    if out.exists():
        return
    result = call(
        "sonnet", None, (EVAL / f"prompts/{variant}.md").read_text(),
        (EVAL / f"inputs/{case['id']}.cutoff.md").read_text(),
    )
    if result is None:
        return
    first = result["text"].splitlines()[0].strip().strip("*`").upper() if result["text"] else ""
    kind = first if first in ("NOTHING", "NOTE", "CARD") else "UNPARSED"
    save(out, {"case": case["id"], "variant": variant, "repeat": repeat, "kind": kind, **result},
         f"{variant}-r{repeat} {case['id']}")


def judge_outputs(case: dict) -> dict[str, list[str]] | None:
    """Distinct output texts for the case, each with the runs that wrote it."""
    texts: dict[str, list[str]] = {}
    for variant in VARIANTS:
        for repeat in REPEATS:
            path = EVAL / f"outputs/{variant}-r{repeat}/{case['id']}.json"
            if not path.exists():
                return None
            text = json.loads(path.read_text())["text"]
            texts.setdefault(text, []).append(f"{variant}-r{repeat}")
    return texts


def run_judge(repeat: int, case: dict) -> None:
    out = EVAL / f"judgments/j{repeat}/{case['id']}.json"
    key_path = EVAL / f"keys/{case['id']}.json"
    if out.exists() or not key_path.exists():
        return
    texts = judge_outputs(case)
    if texts is None:
        return
    rng = random.Random(f"{case['id']}-j{repeat}")
    letters = rng.sample(string.ascii_uppercase, len(texts))
    order = list(texts.items())
    rng.shuffle(order)
    mapping = {letter: runs for letter, (_, runs) in zip(letters, order)}
    map_path = EVAL / f"judge_maps/j{repeat}/{case['id']}.json"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_text(json.dumps(mapping, indent=1))
    outputs = "\n\n".join(
        f"=== OUTPUT {letter} ===\n{text}" for letter, (text, _) in zip(letters, order)
    )
    prompt = fill(
        (EVAL / "prompts/judge.md").read_text(),
        cutoff_facts=(EVAL / f"inputs/{case['id']}.cutoff.md").read_text(),
        all_facts=(EVAL / f"inputs/{case['id']}.all.md").read_text(),
        key=json.dumps(json.loads(key_path.read_text())["key"], indent=1, ensure_ascii=False),
        outputs=outputs,
    )
    result = call("opus", "high", "You judge outputs for an eval.", prompt)
    if result is None:
        return
    match = re.search(r"\{.*\}", result["text"], re.DOTALL)
    try:
        judgment = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        judgment = None
    if judgment is None or set(judgment.get("outputs", {})) != set(mapping):
        print(f"unparsed or incomplete judgment for {case['id']} j{repeat}", flush=True)
        return
    save(out, {"case": case["id"], "repeat": repeat, "map": mapping, "judgment": judgment, **result},
         f"judge j{repeat} {case['id']}")


def main() -> None:
    stage = sys.argv[1]
    only = set(sys.argv[2:])
    cases = [c for c in gathered_cases() if not only or c["id"] in only]
    if stage == "key":
        jobs = [(run_key, case) for case in cases]
    elif stage == "bot":
        jobs = [(run_bot, v, r, case) for r in REPEATS for v in VARIANTS for case in cases]
    elif stage == "judge":
        jobs = [(run_judge, r, case) for r in JUDGE_REPEATS for case in cases]
    else:
        sys.exit(f"unknown stage {stage}")
    with ThreadPoolExecutor(WORKERS[stage]) as pool:
        futures = [pool.submit(job[0], *job[1:]) for job in jobs]
        for future in futures:
            try:
                future.result()
            except Exception as e:  # noqa: BLE001
                print(f"job failed: {e!r}", flush=True)
    commit(f"eval2: Stage {stage} done.")
    if stop.is_set():
        sys.exit("stopped early (model gate or deadline)")


if __name__ == "__main__":
    main()
