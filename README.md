# Triage bot eval 1: ready-comment check

Does an author's comment on a "not ready" PR ask maintainers for another look?

- `cases.json`: 240 author comments on PRs labeled "not ready", June–September 2026, with the maintainer comment before each one and what maintainers did in the next 14 days.
- `prompts/key.md`: Opus (high effort) writes the answer key.
- `prompts/v1.md`–`v3.md`: Sonnet variants, each run twice.
- `./run.py key`, then `./run.py bot`, then `./score.py`.
