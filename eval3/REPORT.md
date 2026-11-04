# Reviewer-suggestion eval (eval3)

**Question:** when a PR gets "maintainer review" and nobody is assigned,
can the triage bot suggest the reviewer the triager actually picked?

**Short answer: yes, mostly.** Variant v2 (who is already engaged first)
puts the real assignee first on 79% of cases. It's in the top 3 on 85%.
When it misses, the Opus judge called 90% of its picks reasonable. Both
no-model baselines are far behind.

## Setup

- **100 cases**: contributor PRs from 2026-05 to 2026-10 that got "maintainer
  review", with someone other than the author assigned within 1 hour. The
  input is the bot's view of the PR just before the hand-off.
- **Two prompts** (`prompts/`): **v1_file_history** ranks by who changed
  these files, then by who is in the discussion. **v2_area_activity**
  decides the area first, then prefers maintainers already engaged with the
  work, then recent activity. Both get the maintainer list with names, so
  git author names can be mapped to logins.
- **Bot runs**: Sonnet, each variant on every case, twice (400 outputs, in
  `runs/`). **Judge**: Opus, once for each distinct (PR, suggested login)
  top-1 miss (44 pairs, in `judge/`, with the context it saw in
  `judge_context/`).

## Results

| | Top-1 | Top-3 | Top-1 misses judged reasonable |
|---|---|---|---|
| v1 file history, run 1 / run 2 | 70 / 69 | 84 / 86 | 23 of 30 / 20 of 31 |
| v2 area + engagement, run 1 / run 2 | **78 / 80** | 84 / 85 | 18 of 22 / 18 of 20 |
| Baseline (a): first file author who is a maintainer | 20 | 20 (one name only) | not judged |
| Baseline (b): most-assigned maintainer on the same top-level path, earlier hand-offs | 9 | 32 | not judged |

- **Spread between runs is small.** v1 moves by 1 point (top-1) and 2 points
  (top-3). v2 moves by 2 and 1. v2 is also more stable: it gives the same
  top-1 in both runs on 95 cases (v1: 89).
- **Counting a reasonable miss as fine**, v2 gives a usable first name on
  96–98 cases and v1 on 89–93.
- **Where the signal comes from:** on 46 cases, a maintainer comment in the
  input already @-mentions the eventual assignee. Usually it's a triager
  asking that person to review, just before adding the label. v2 gets
  42–44 of those 46; v1 gets 37. On the other 54 cases, v2 gets 36 and v1
  gets 32–33. So most of v2's lead comes from not overriding an explicit
  request with file history.
- **Two cases can't be hit.** #40096 and #40097 went to 0xthedance, who
  isn't in maintainers.txt.
- **Baseline (b) is weak because top-level paths are too coarse.** Almost
  every PR touches `web/` or `zerver/`, so it mostly picks whoever gets the
  most hand-offs overall.
- **Never broke a rule:** none of the 400 outputs suggested the PR author or
  a login outside the list.

## Example misses

- **#39878**: all 4 runs said @prakhar1144 (who owns the stacked base PR).
  The real pick was @laurynmm, and karlstolley had tagged her for maintainer
  review in a comment. *Not reasonable.* This is the clearest miss that v2
  still makes.
- **#40398**: 3 runs said @mateuszmandera, from an earlier attempt. The
  assignee was @benprew, whom karlstolley had asked by name. *Not
  reasonable.*
- **#40376**: all runs said @alexmv. The assignee was @benprew. Tim had named
  alexmv as the right person for the issue, and alexmv is the top committer
  to these nginx files. *Reasonable.*
- **#40418**: all runs said @amanagr. The assignee was @evykassirer. Aman is
  the top committer to `recent_view_ui.ts` and got all earlier hand-offs on
  it. *Reasonable.*
- **#40096**: all runs said @Niloth-p. The assignee was 0xthedance, who isn't
  in the maintainer list. Niloth-p has recent commits to these webhook
  files. *Reasonable.*

Most unreasonable v1 misses follow one pattern: a maintainer asked a
specific person to review, and v1 ranked the top committer above them anyway
(#39770, #39867, #40065, #40113, #40162, #40192, #40218, #40241).

## Recommendation

**Use v2 (area and who is already engaged first).** Compared with v1, it has
about 9 points more top-1, the same top-3, and more stable output. Its misses
are judged reasonable more often (36 of 42 vs 43 of 61). It also respects
explicit "@X, could you review?" requests, which are the strongest signal a
triager leaves. Both baselines are far below either prompt. Possible
follow-up: add one line to v2 saying that a maintainer's explicit request
for a named reviewer wins over everything else. That would target misses
like #39878 and #40398.

## Caveats

- **How the subagents got their input.** The prompt was put inline in each
  subagent's instructions. But the PR inputs (1.8 MB in total) were too
  large to inline 400 times from the orchestrating session. Subagents can't
  start their own subagents, so each bot subagent was told to read exactly
  its own input file (copied to a scratch folder with nothing else in it)
  and nothing more. Judges read the input and their judge-context file the
  same way. Each bot subagent handled 10 cases (one variant, one run);
  each judge handled about 5 misses. Cases were scored separately.
- **Ground truth is one triager's choice.** Several maintainers could often
  have done the review, which is why the judged "reasonable" share matters.
- **What the judge saw.** The judge knew the real assignee, and saw earlier
  hand-offs touching the same files and directories.

Files: `scores.json` (per-case suggestions and hit counts), `baselines.json`,
`judged.json`, `analysis.json`, scripts in `scripts/`. To redo the scoring,
run `python3 scripts/score.py && python3 scripts/judged.py`. Bot and judge
calls are only needed for missing files in `runs/` and `judge/`.
