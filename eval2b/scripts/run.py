#!/usr/bin/env python3
"""Run eval 2b: revisions of the v3 second-look prompt.

  run.py bot <variant> <tune|heldout> <repeat>...
      Sonnet runs eval2b/prompts/<variant>.md on every case of the set.
  run.py judge-tune <variant>
      Opus judges, once per tune case, the revision's run 1 next to eval 2's
      v3-r1 output for the same case (the baseline), letters and order random.
  run.py judge-heldout <variant>
      Opus judges, twice per held-out case with fresh letters and order, the
      four outputs v3-r1, v3-r2, <variant>-r1, <variant>-r2.

Calls are made as in eval2/scripts/run.py: one fresh `claude -p` with no
tools, settings, skills, MCP servers or saved session; the model each call
reports is checked (Sonnet for the bot, Opus for the judge) and the run stops
on anything else. The eval 2 keys and judge prompt are reused. Work that
already has a result is skipped. The excluded case is never run or judged.
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

HERE = Path(__file__).resolve().parent.parent
EVAL2 = HERE.parent / "eval2"
ROOT = HERE.parent
ALLOWED_MODELS = {"sonnet": "claude-sonnet-", "opus": "claude-opus-"}
WORKERS = 6
COMMIT_EVERY = 20
NO_TOOLS = (
    "Don't read files or use tools: everything you need is in this message. "
    "Reply with the output only."
)
TRAILER = ("\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
           "Claude-Session: https://claude.ai/code/session_01NWiGA13A5WcbSBdMxG7R2G")
SPLIT = json.loads((HERE / "split.json").read_text())

lock = threading.Lock()
done_since_commit = 0
stop = threading.Event()


def commit(message: str) -> None:
    with lock:
        subprocess.run(["git", "add", "eval2b"], cwd=ROOT, check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
            return
        subprocess.run(["git", "commit", "-qm", message + TRAILER], cwd=ROOT, check=True)
        result = subprocess.run(["git", "push", "-q", "-f", "origin", "HEAD:triage-eval2b"],
                                cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"push failed: {result.stderr.strip()[:200]}", flush=True)


def call(model: str, effort: str | None, system: str, user: str) -> dict | None:
    if stop.is_set():
        return None
    command = [
        "claude", "-p", "--model", model, "--system-prompt", system,
        "--tools", "", "--setting-sources", "", "--strict-mcp-config",
        "--no-session-persistence", "--output-format", "json",
    ]
    if effort:
        command += ["--effort", effort]
    for attempt in range(3):
        result = subprocess.run(command, input=user + "\n\n" + NO_TOOLS, capture_output=True,
                                text=True, timeout=1200, cwd="/tmp")
        if result.returncode == 0:
            break
        print(f"call failed (try {attempt + 1}): {result.stderr.strip()[:300]} {result.stdout[:300]}",
              flush=True)
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
    print(f"saved {path.relative_to(HERE)}", flush=True)
    with lock:
        done_since_commit += 1
        due = done_since_commit >= COMMIT_EVERY
        if due:
            done_since_commit = 0
    if due:
        commit(f"eval2b: Results up to {label}.")


def case_ids(name: str) -> list[str]:
    return [c for c in SPLIT[name] if c not in SPLIT["excluded"]]


def output_path(run: str, cid: str) -> Path:
    """`run` is "<variant>-r<n>"; "eval2:<variant>-r<n>" means an eval 2 output."""
    if run.startswith("eval2:"):
        return EVAL2 / f"outputs/{run[6:]}/{cid}.json"
    return HERE / f"outputs/{run}/{cid}.json"


def run_bot(variant: str, repeat: int, cid: str) -> None:
    out = output_path(f"{variant}-r{repeat}", cid)
    if out.exists():
        return
    result = call("sonnet", None, (HERE / f"prompts/{variant}.md").read_text(),
                  (EVAL2 / f"inputs/{cid}.cutoff.md").read_text())
    if result is None:
        return
    first = result["text"].splitlines()[0].strip().strip("*`").upper() if result["text"] else ""
    kind = first if first in ("NOTHING", "NOTE", "CARD") else "UNPARSED"
    save(out, {"case": cid, "variant": variant, "repeat": repeat, "kind": kind, **result},
         f"{variant}-r{repeat} {cid}")


def run_judge(name: str, repeat: int, runs: list[str], cid: str) -> None:
    out = HERE / f"judgments/{name}/j{repeat}/{cid}.json"
    if out.exists():
        return
    texts: dict[str, list[str]] = {}
    for run in runs:
        path = output_path(run, cid)
        if not path.exists():
            return
        texts.setdefault(json.loads(path.read_text())["text"], []).append(run)
    rng = random.Random(f"eval2b-{name}-{cid}-j{repeat}")
    letters = rng.sample(string.ascii_uppercase, len(texts))
    order = list(texts.items())
    rng.shuffle(order)
    mapping = {letter: r for letter, (_, r) in zip(letters, order)}
    outputs = "\n\n".join(f"=== OUTPUT {letter} ===\n{text}"
                          for letter, (text, _) in zip(letters, order))
    template = (EVAL2 / "prompts/judge.md").read_text()
    values = {
        "cutoff_facts": (EVAL2 / f"inputs/{cid}.cutoff.md").read_text(),
        "all_facts": (EVAL2 / f"inputs/{cid}.all.md").read_text(),
        "key": json.dumps(json.loads((EVAL2 / f"keys/{cid}.json").read_text())["key"],
                          indent=1, ensure_ascii=False),
        "outputs": outputs,
    }
    for k, v in values.items():
        template = template.replace("{" + k + "}", v)
    result = call("opus", "high", "You judge outputs for an eval.", template)
    if result is None:
        return
    match = re.search(r"\{.*\}", result["text"], re.DOTALL)
    try:
        judgment = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        judgment = None
    if judgment is None or set(judgment.get("outputs", {})) != set(mapping):
        print(f"unparsed or incomplete judgment for {name} {cid} j{repeat}", flush=True)
        return
    save(out, {"case": cid, "repeat": repeat, "map": mapping, "judgment": judgment, **result},
         f"judge {name} j{repeat} {cid}")


def main() -> None:
    stage = sys.argv[1]
    if stage == "bot":
        variant, set_name, repeats = sys.argv[2], sys.argv[3], [int(r) for r in sys.argv[4:]]
        jobs = [(run_bot, variant, r, cid) for r in repeats for cid in case_ids(set_name)]
    elif stage == "judge-tune":
        variant = sys.argv[2]
        jobs = [(run_judge, f"tune-{variant}", 1, ["eval2:v3-r1", f"{variant}-r1"], cid)
                for cid in case_ids("tune")]
    elif stage == "judge-heldout":
        variant = sys.argv[2]
        runs = ["v3-r1", "v3-r2", f"{variant}-r1", f"{variant}-r2"]
        jobs = [(run_judge, f"heldout-{variant}", r, runs, cid)
                for r in (1, 2) for cid in case_ids("heldout")]
    else:
        sys.exit(f"unknown stage {stage}")
    with ThreadPoolExecutor(WORKERS) as pool:
        futures = [pool.submit(job[0], *job[1:]) for job in jobs]
        for future in futures:
            try:
                future.result()
            except Exception as e:  # noqa: BLE001
                print(f"job failed: {e!r}", flush=True)
    commit(f"eval2b: {' '.join(sys.argv[1:])} done.")
    if stop.is_set():
        sys.exit("stopped early (model gate)")


if __name__ == "__main__":
    main()
