# Eval 2c: facts-only second look (v3f) vs v3

## What was run

- Bot: `prompts/v3f.md` on all 60 eval2 cases, twice (Sonnet, one subagent
  per case and run, given only the case's `cutoff.md`).
- Judge: `prompts/judge_facts.md` (Opus). For each case, one judge call saw
  four outputs under random letters in random order: v3f r1, v3f r2, and
  eval2's v3 r1 and v3 r2. Each case was judged twice with fresh letters
  and order. 120 judgments, all parsed.
- Case 39863-5344084962 is left out of all scores (its key is wrong). That
  leaves 59 cases, so 236 scored outputs per prompt.

## Results

| | v3f | v3 |
| --- | --- | --- |
| Mean facts_score (1–10) | 6.50 | 6.59 |
| Bot run 1 / run 2 | 6.57 / 6.43 | 6.54 / 6.64 |
| Judge repeat 1 / 2 | 6.47 / 6.53 | 6.54 / 6.64 |
| Wrong facts per output | 0.37 | 0.42 |
| Missed key items per output | 1.42 | 1.44 |
| Outputs scored 4 or lower | 13% | 18% |
| Words per output (all) | 83 | 125 |
| Words in the New/Missing part | 83 | 55 |

Paired difference per case (v3f − v3, each side averaged over 2 runs × 2
judge repeats): **−0.09 ± 0.23** (mean ± SE, n = 59). v3f is better on 24
cases, v3 on 30, tied on 5. The two judge repeats differ by 0.31 points
per output on average.

v3f chose NOTHING 2 times out of 120 (both runs of 40177-5954127181) and
CARD 0 times; the other 118 were NOTEs.

## Where v3f lost and won

- Worst: 40177-5954127181. Both runs said NOTHING ("only asks again, no
  new push"), but the author had updated the prior-work section and the
  key lists missing before and dark-theme screenshots. Scores 1–2.
- 40042-6183881101 and 40042-6183102956: v3f doubted the main fix
  ("commit bodies can't be confirmed") and padded "Still missing" with
  items the feedback never asked for. v3 said nothing blocking remained,
  which matched the key.
- Best: 40257, 40096, 39865, 40085. v3f named the missing item that v3
  passed over on its way to a hand-off verdict.

## Example v3f notes

**Good** (40191-5798802930 r1, 10.0):
> New: One push since the feedback: the Home Assistant docs commit was removed (the work moved to the separate open PR #40197), and the author says both commit messages were reworded; the code is otherwise unchanged.
> Still missing: nothing from the last feedback; the reworded commit message bodies and the screenshots in #40197 can't be checked from the input (only commit titles and the author's claim are visible), and CI status is unknown.

**Bad** (39785-5037857009 r2, 2.5): it took the author's screenshot
comment as meeting the request and missed every gap in the key.
> New: The author posted a before/after dark mode screenshot as a comment (not added to the PR description), with no new push.
> Still missing: nothing from the last feedback.

**Typical** (39540-4708052713 r1, 7.0, the median): accurate, but it
misses the dark-theme screenshot mismatch and runs past three items.
> New: The author pushed 2 more times, but the size (+37/-0 in 1 file), the files and the commit messages are unchanged, and then asked a different person (Asteriskkkk) to review.
> Still missing: Commit history cleanup that laurynmm asked for; the commit list still shows the "Merge branch 'main'" commit next to the fix commit. Several self-review checklist items are still unchecked (remaining decisions and concerns, tests, responsiveness and internationalization, strings, corner cases). CI results are not available to confirm the author's claim that checks pass.

## Recommendation

**Ship v3f.** Its facts are as accurate as v3's: the gap is −0.09 ± 0.23,
with slightly fewer wrong facts and fewer low scores. Two fixes to make
first: tell it not to say NOTHING when the author edited the description,
and keep "Still missing" to what the feedback asked for. That second fix
should also shorten the facts part, which is longer than v3's.

## Files

- `prompts/`: v3f and the judge prompt (unchanged).
- `outputs/v3f-r1/`, `outputs/v3f-r2/`: the bot outputs (`.md`).
- `judge_maps/j<n>/`: the letter → run mapping for each judgment.
- `judgments/j<n>/`: the judge's raw JSON.
- `results/summary.json`: every number above, and all v3f outputs ranked.
- `scripts/`: `prep_bot.py`, `prep_judge.py` (they build the scratch input
  folders and letter maps), `check_judgments.py`, `score.py`, `commit.sh`.

Every model call was an Agent-tool subagent in one session, with the
prompt inline and only that call's input files copied to an otherwise
empty scratch folder. Bot calls asked for model "sonnet" and judge calls
for "opus". The subagent results don't report which model actually
served them, so that couldn't be checked independently.
