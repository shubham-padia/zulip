# Eval 2: second look at a "not ready" PR

## What was tested

When an author comments on a "not ready" PR to ask for another look, the
bot posts NOTHING, a short NOTE under the PR's first card, or a new CARD.
Three prompt variants (`prompts/v1.md`–`v3.md`) were each run twice on 60
cases with Sonnet. Opus wrote the answer keys and judged.

- **v1**: NOTE by default. A short "what changed" line and a table of 1–4
  points. CARD only if the first card would now mislead.
- **v2**: a checklist row for every request in the feedback. CARD whenever
  the code changed a lot (commits replaced, files added or removed).
- **v3**: very short. One verdict line, one "New: … Missing: …" line, the
  next step and the reply. CARD is rare. NOTHING also when the author only
  asks again with nothing new.

## Cases

There are 60 author comments from eval 1 whose key says "asks for another
look". They come from 55 PRs, with at most 2 per PR. What happened next:
the triager removed "not ready" (12), a maintainer replied (28), the PR
was closed unmerged within 14 days (10), or nothing happened (10).

Each case was gathered as of the author's comment, following the cutoff
rules in `tools/triage_bot/evals/README.md`. The bot input ends with a
"Second look" section with the "not ready" label event and the last
maintainer comment before the author's comment. It also shows the code
changes since that comment (the head commit at both times from CI runs
and force pushes, then commits, files and size), and the new comment.
The key also had the PR gathered with no cutoff.

## Keys

All 60 keys say **NOTE**. These are real authors asking for review after
feedback, and none of the PRs changed enough for a new card. So the
NOTHING/NOTE/CARD choice mostly checks that a variant doesn't post a CARD.
The useful measure is whether the note recommends the right triager
action. The keys' actions are hand off (28), more feedback (26) and
close (6). Ten of these were inferred, because maintainers did nothing.

Spot check: I read 15 keys. Key 39863-5344084962 is wrong. It says the
commit summary must not end with a period, but Zulip summaries do end
with one. So the "hand off" outputs for that case were probably right.

## Results

Scores are 1–10, averaged over 2 bot runs × 2 judge repeats (240 scored
outputs per variant). The overall score is the mean of the four parts.

| | v1 | v2 | v3 |
| --- | --- | --- | --- |
| Decision accuracy (NOTHING/NOTE/CARD vs key) | 98% (2 CARD) | 89% (13 CARD) | **100%** |
| Triager action matches key | 64% | 61% | **67%** |
| Decision score | 7.02 | 6.65 | **7.20** |
| Accuracy (what changed / missing) | **5.77** | 5.70 | 5.60 |
| Reply score | 5.67 | 5.68 | **5.75** |
| Brevity score | 6.80 | 6.90 | **8.45** |
| **Overall** | 6.31 | 6.23 | **6.75** |
| Overall, judge repeat 1 / 2 | 6.31 / 6.32 | 6.20 / 6.27 | 6.74 / 6.76 |
| Overall, bot run 1 / 2 | 6.29 / 6.34 | 6.32 / 6.15 | 6.78 / 6.73 |
| Wrong facts per output | 0.31 | 0.37 | 0.37 |
| Words per output | 196 | 182 | 125 |

Paired differences in overall score, per case (mean ± SE): v3 − v1 =
+0.44 ± 0.13, v3 − v2 = +0.52 ± 0.18, v1 − v2 = +0.08 ± 0.18. The two
judge repeats agree within 0.07, and the two bot runs within 0.17.

v3 wins mostly on brevity. On accuracy and replies, the three variants
are within 0.2 of each other. No variant ever posted NOTHING.

The most common rule failure is `filler_point`: 95 for v1, 87 for v2 and
9 for v3. The tables add rows the triager doesn't act on, such as "CI
passed" or "no conflicts". Next is `asks_for_done_work`: 8, 14 and 8.

### The shared weakness: the action

All three variants get the action wrong about a third of the time, in
the same ways:

- **Missed closes.** For the 6 close cases, v1 and v2 never said close.
  They said "more feedback" or "hand off" instead. v3 said close 4 times
  out of 24.
- **Hand off vs. more feedback.** Each variant hands off 20–28 of 100
  "more feedback" outputs, and asks for more work in 28–34 of 108
  "hand off" outputs. The bot takes the author's "done" at face value
  for problems that are about the approach (API design, not on track,
  competing PRs). It also blocks on small leftovers that the triager
  ignored.

This is why reply scores are low (about 5.7): a reply that goes with the
wrong action scores 1–3.

## Examples

Scores are overall, averaged over the two judge repeats.

**v1, good**
- 39622-5419621157 r1 (8.75): keeps "not ready" until the first reviewer
  signs off, and the reply asks the author to answer that reviewer's
  comments.
- 39935-5355372259 r1 (8.75): keeps "not ready", and asks to clean up the
  commits with a link to the commit discipline guide. This matches the
  maintainer's later reply.
- 40171-5795222359 r1 (9.0): the screenshots asked for are in, so it hands
  off to Niloth-p with one thank-you line.

**v1, bad**
- 40013-5589724033 r2 (3.4): hands off a PR that adds API changes, which
  needed design discussion and docs. It also says the issue lost "help
  wanted", which nothing in the input shows.
- 39945-5415679206 r1 (3.75): asks laurynmm to review a PR that competes
  with two PRs already in review. It was closed.
- 40040-6192384462 r1 (3.75): hands off a PR that the maintainer closed as
  the wrong approach.

**v2, good**
- 39929-5293011728 r1 (9.1): hand off to sahil839, "No reply needed."
- 40042-6183102956 r1 (9.0): hand off with one reviewer ping. The PR was
  merged the same day.
- 39784-5100999626 r1 (8.75): keeps "not ready", and asks for paired
  before/after screenshots, including the whitespace case, with the guide
  link.

**v2, bad**
- 40168-5775859018 r1 (2.9): "Ready for review" with a 6-row table, but
  the before/after screenshots the issue requires are missing. It was
  closed as not on track.
- 39945-5415679206 r2 (3.25): hands off a competing PR, names the
  contributor, and marks the "how does this relate to other PRs" request
  as done when it wasn't.
- 40048-5481098127 r2 (3.4): recommends closing where the PR only needed
  the API changelog and feature-level updates.

**v3, good**
- 40171-5795222359 r2 (9.5): "Ready for review — the requested before/after
  screenshots are now in the description". One "New:" line, assigns
  Niloth-p, and a one-line reply.
- 39822-5091673928 r2 (9.25): a short hand-off with one reviewer ping. The
  maintainer added "integration review" the same way.
- 40042-6183102956 r2 (9.1): a short hand-off, matching the merge.

**v3, bad**
- 40085-5574954238 r2 (3.1): closes because the issue "no longer has help
  wanted". But the issue was assigned to the author, and a maintainer
  handed the PR off for review.
- 40168-5775859018 r2 (3.4): "nothing blocking, ready for review", but the
  required before/after screenshots were missing. It was closed.
- 40030-5442478190 r1 (3.6): says the template is filled in and hands off.
  The maintainer re-added "not ready" and asked the author to follow the
  reviewable-PR guide.

## Recommendation

**Use v3.** It is the best on every measure except accuracy, where all
three are within 0.2. It is about a third shorter than v1 and v2, never
posts a CARD by mistake, and is the only variant that ever recommended a
close. Triagers already read the first card, so the short "New: …
Missing: …" line is what they need. v2's per-request checklist doesn't
make the facts more accurate, and its CARD rule fires on ordinary
rebases.

Before shipping, work on the action, which is wrong about a third of
the time for every variant:
- Tell the bot that "done" doesn't settle approach problems. If a
  maintainer questioned the approach, the API design, or a competing PR,
  the note should say so and not hand off.
- Add close cases: a PR that competes with one already in review, and a
  PR a maintainer called not on track.
- These cases never needed NOTHING or CARD. Before relying on those
  branches, test them on cases that do: comments that only acknowledge
  feedback, and PRs rewritten after feedback.

Tune these changes on some cases and check them on others. The 60 cases
here can serve as the held-out set.

## Files

- `cases.json`: the 60 cases, with `group`.
- `inputs/`: the bot input (`.cutoff.md`) and the full facts (`.all.md`).
- `gather/`: how each cutoff view was built.
- `keys/`, `outputs/<variant>-r<n>/`, `judgments/j<n>/`, `judge_maps/`.
- `results/summary.json`: all the numbers, and every output ranked.
- `scripts/`: `select_cases.py`, `gather_case.py`, `run.py` (`key`, `bot`,
  `judge`; reruns only do missing work), `score.py`, `show.py`.

Each model call was one fresh `claude -p` with no tools, settings, skills
or MCP servers (as in eval 1). A model gate stops the run if a call
reports any model other than Sonnet (bot) or Opus (key, judge). Cost: keys
$10.80, bot runs $9.81, judging $28.94.
