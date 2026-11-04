# Eval 2b: improving how v3 picks the triager action

## Goal

Eval 2 picked prompt v3 for the bot's second look at a "not ready" PR. Its
recommended action (hand off for review / more feedback / close) was wrong
about a third of the time. This eval tried to fix that without making v3
longer or less accurate.

## Setup

- **Split**: the 60 eval 2 cases were split 30/30 into a tune set and a
  held-out set, stratified by `group` (seed 20261104, `scripts/split.py`,
  `split.json`). Each set has 14 replied, 6 removed, 5 closed and 5
  no-action cases. Case 39863-5344084962 has a known-wrong key and was not
  run or scored, so the tune set has 29 scored cases.
- **Models**: every call was a fresh `claude -p` with no tools, as in
  eval 2. Bot runs used Sonnet and judging used Opus (high effort). The
  model gate checked the reported model on every call, and it never
  fired. Eval 2's keys and judge prompt were reused unchanged.
- **Tune scoring**: each revision ran once per tune case. Opus judged it
  side by side with eval 2's v3 run 1 output for the same case, once,
  with random letters and order.
- **Held-out scoring**: the best revision and the original v3 ran twice
  each per case. Opus judged all four outputs together, twice, with fresh
  letters and order (120 scored outputs per prompt).

## The revisions

All three revisions keep v3's output format and add one short section,
"How to choose the action".

- **v3a** added an ordered checklist. (1) Should the PR still exist?
  Close if a maintainer called it wrong or off track, or if it competes
  with a PR already in review. (2) Is a design or API question still open?
  (3) Can a reviewer check that it works (linked issue, screenshots that
  show the bug)? (4) Otherwise hand off, and don't block on small
  leftovers. It also said a missing "help wanted" label is no reason to
  close once a maintainer has engaged with the PR.
  *Why*: v3 took "done" at face value. It closed two PRs over "help wanted"
  that maintainers were already reviewing, and it waved through a PR with
  no linked issue and screenshots that didn't show the bug.
- **v3b** started again from v3, because v3a made things worse. It says
  **the feedback the author is answering sets the bar**. Hand off when
  every item the feedback asked for is done, and don't invent new
  blockers. Give more feedback when an item that was asked for isn't
  done, or when a question about the change itself (whether it's wanted,
  the approach, the API design, competing PRs) is unanswered. For a PR
  that competes with one in review, ask for a comparison. Close only when
  a maintainer already said it's wrong or off track. It kept v3a's "help
  wanted" exception.
  *Why*: v3a's reading of its tune outputs showed three problems. Its
  "competing PR → close" rule fired where maintainers had asked for a
  comparison (3 cases). Its "evidence" step made up blockers the triager
  never raised, such as screenshots for a PR where nobody asked for them.
  Its "small leftovers" step waved off commit cleanup that *was* the
  feedback's ask.
- **v3c** was v3b plus two changes. An ask counts as done only if it meets
  the linked guide's standard and answers the concern behind it, so a
  discussion that was only started, a comparison that misses the point,
  or screenshots that don't show the fix don't count. And a pointer to
  the contributor guides doesn't count as a maintainer engaging.
  *Why*: v3b counted an attempt as done. Examples: an #api design topic
  that had only been opened, a comparison that ignored "this isn't
  viable", and screenshots whose own test showed the fix failing. It also
  lost a correct close, because a generic "read the guide" comment
  counted as engagement.

## Tune-set results (29 cases, 1 bot run, 1 judging)

v3 is eval 2's v3 run 1, judged in the same call as each revision.

| | v3a | v3b | v3c |
| --- | --- | --- | --- |
| Action accuracy, revision / v3 | 48% / 69% | 62% / 69% | 55% / 69% |
| Overall, revision / v3 | 6.17 / 6.26 | 6.35 / 6.34 | 6.21 / 6.28 |
| Paired overall difference (mean ± SE) | −0.09 ± 0.48 | +0.01 ± 0.32 | −0.08 ± 0.25 |
| Accuracy score, revision / v3 | 5.48 / 5.03 | 5.00 / 5.28 | 5.28 / 4.97 |
| Brevity score, revision / v3 | 8.24 / 7.93 | 8.41 / 7.97 | 7.93 / 8.03 |
| Wrong facts per output, revision / v3 | 0.48 / 0.69 | 0.45 / 0.52 | 0.52 / 0.79 |
| Words per output (v3: 124) | 124 | 109 | 128 |

No revision beat v3 on action accuracy on the tune set. Each fixed 3–5
cases and broke about as many. v3b was the best revision: the same overall
score as v3, the shortest outputs and the fewest wrong facts. So v3b went
to the held-out set.

## Held-out results: v3b vs v3 (30 cases, 2 bot runs × 2 judgings)

| | v3 | v3b |
| --- | --- | --- |
| **Action accuracy** | 57% | **65%** |
| Action accuracy, bot run 1 / 2 | 60% / 53% | 67% / 63% |
| NOTHING/NOTE/CARD matches key | 100% | 100% |
| **Overall** | **6.63** | 6.55 |
| Overall, bot run 1 / 2 | 6.78 / 6.48 | 6.53 / 6.57 |
| Overall, judging 1 / 2 | 6.72 / 6.55 | 6.60 / 6.50 |
| Decision score | 6.78 | 7.07 |
| Accuracy score | **5.98** | 5.27 |
| Reply score | 5.79 | 5.84 |
| Brevity score | 7.98 | 8.03 |
| Wrong facts per output | **0.38** | 0.53 |
| Words per output | 124 | **113** |

Paired per-case differences (v3b − v3, mean ± SE over 30 cases): action
accuracy **+8 ± 7 points**, overall score **−0.08 ± 0.26**. Neither is
clearly different from zero.

Where the action changed (counts over the 4 judged outputs per case):

| Key → output | v3 | v3b |
| --- | --- | --- |
| hand_off → hand_off | 42 / 64 | 56 / 64 |
| more_feedback → more_feedback | 26 / 40 | 22 / 40 |
| close → close | 0 / 16 | 0 / 16 |
| close → hand_off | 2 | 8 |

v3b hands off more often. That fixes most of v3's "blocks on leftovers"
errors, but it costs some "more feedback" cases, and it hands off two PRs
that were later closed. **Neither prompt recommended closing any of the 4
held-out close cases.** v3b also has a new failure: in 14 outputs, all of
them hand-offs, the judge found that the reply contradicts the verdict.
The verdict says hand off, but the reply also asks the author for more
work, such as a squash. v3 had this failure in 3 outputs.

### Cases v3b fixed

- **40201-6155498168**: the only ask was a passing CI run, and CI now
  passes. v3 blocked on "no linked issue, so it's unclear this work was
  approved", which nobody had asked about. v3b: "Ready for review — CI now
  passes, which was the only thing asked for" (overall 4.7 → 8.1).
- **40096-6055469654**: v3 blocked because the fixes were in separate
  commits. The triager handed off hours later. v3b handed off (3.9 → 6.9).
- **40041-5479840283**: the ask was to link a discussion, and the author
  linked one. v3 blocked because no maintainer had replied in the thread
  yet. v3b handed off (4.3 → 7.4).

Also fixed: 39865-5194201765 (2 of 4 → 4 of 4 right) and 40097-6055464855
(2 of 4 → 4 of 4 right).

### Cases v3b broke

- **39694-4914523135**: the alignment fix was pushed, but the follow-up
  fixes sat in separate commits. The maintainer asked for commit cleanup
  and more design work. v3 kept "not ready"; v3b handed off (7.6 → 5.1).
- **40168-5775859018** (key: close): the maintainer judged the PR not on
  track and closed it. v3 said more feedback; v3b said "Ready for review:
  the feedback asked for a proper PR presentation, and that is now done"
  (5.8 → 3.3).
- **39945-5415679206** (key: close; it competes with two PRs already in
  review): v3 handed off 2 of 4 times, and v3b 4 of 4.
- **39481-4711243565**: v3b handed off 2 of 4 times where the key says
  more feedback.

## Recommendation

**Keep v3 for now. Don't ship v3b as it is.** v3b's +8-point action gain
is within noise (± 7), and it didn't show up on the tune set, where v3b
was 7 points *worse*. It costs 0.7 points of accuracy and 40% more wrong
facts, and its hand-off replies often still ask for work. Its one clear
lesson is real: **judge the PR against what the feedback asked for, and
don't add blockers.** That is what fixed 40201, 40096 and 40041. But on
its own it makes the bot trust the author's "done" more, which is the
failure we were trying to fix.

What I'd try next:
- Keep v3b's "the feedback sets the bar" idea, and add one line: a reply
  that goes with a hand-off never asks the author for more work. This
  fixes the new `reply_contradicts_verdict` failures without changing
  any action.
- Closing is still almost never recommended (0 of 16 held-out outputs for
  either prompt). In these cases, the maintainers' reasons to close came
  from their own reading of screenshots or approach after the author's
  comment. The bot may not be able to infer that from the cutoff input.
  It may be better to stop expecting "close" from the second look, and
  measure hand off vs more feedback alone.
- Single runs move action accuracy by up to 7 points, and 10 of the 60
  keys are inferred. Future tuning needs at least 2 bot runs per revision,
  or more cases, to tell a real change from noise.

**Still untested:** all 60 keys say NOTE, so the NOTHING and CARD branches
of every prompt are untested. Before relying on them, add cases that need
them: comments that only acknowledge feedback, and PRs rewritten after
feedback.

## Files

- `split.json`: the tune and held-out case lists, the seed, and the
  excluded case.
- `prompts/`: `v3.md` (a copy of eval 2's), `v3a.md`, `v3b.md`, `v3c.md`.
- `outputs/<variant>-r<n>/<case>.json`: bot outputs. `v3a`, `v3b` and
  `v3c` run 1 cover the tune set. `v3` runs 1–2 and `v3b` runs 1–2 cover
  the held-out set.
- `judgments/tune-<variant>/j1/` and `judgments/heldout-v3b/j{1,2}/`: the
  judge's JSON, with the letter-to-run map.
- `results/tune-v3a.json`, `results/tune-v3b.json`, `results/tune-v3c.json`
  and `results/heldout-v3b.json`: all the numbers and the per-case actions.
- `scripts/split.py`, `scripts/run.py` (`bot`, `judge-tune`,
  `judge-heldout`; a rerun only does missing work) and `scripts/score.py`.
