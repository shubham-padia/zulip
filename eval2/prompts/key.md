You prepare the scoring targets ("key facts") for an eval of a triage bot
for the Zulip open-source project.

The bot's new step works like this. A triager labeled a contributor's pull
request "not ready" and gave feedback. When the PR's author comments to ask
for another look, the bot takes a "second look" and posts one of:
- NOTHING: nothing is posted, because no maintainer needs to see this.
- NOTE: a short note under the PR's first card in the maintainers' Zulip
  topic: what changed, what's still missing, the next step, and a reply to
  paste on GitHub.
- CARD: a full new card about the PR (a summary of what it changes for
  users, points, a reviewer, the next step and a reply), because the PR
  changed so much that the first card would mislead.
The triager reading the note or card then decides to:
- hand_off: remove "not ready", add "maintainer review" (or "integration
  review"), and assign a reviewer;
- more_feedback: keep "not ready" and tell the author what is still
  missing;
- close: close the PR.

What was known when the author commented (what the bot sees). Its "Second
look" section has the feedback the author answered, the code changes since
then, and the author's new comment:

<cutoff_facts>
{cutoff_facts}
</cutoff_facts>

Everything about the PR up to now, including what happened later:

<all_facts>
{all_facts}
</all_facts>

What maintainers did in the 14 days after the author's comment, from the
labels and comments: {what_happened_next}

Reply with only a JSON object of this shape:

{"decision": "NOTHING|NOTE|CARD",
 "decision_why": "one sentence",
 "triager_action": "hand_off|more_feedback|close|none",
 "action_source": "observed|inferred",
 "action_why": "one sentence",
 "changed": ["what the author changed or answered since the feedback, one short sentence each"],
 "still_missing": ["what is still missing at the time of the comment, one short sentence each"],
 "reply_ask": "one sentence: the main thing the reply must say or ask, or \"no reply needed\"",
 "must_have": [{"id": "f1", "fact": "...", "decisive": true, "at_cutoff": true}]}

Rules:
- `triager_action`: take it from what maintainers did after the comment.
  "not ready" removed, or a reviewer assigned, or the PR reviewed with no
  request for more work, or merged → `hand_off`. A maintainer asked for
  changes, screenshots, tests or answers → `more_feedback`. Closed unmerged
  by a maintainer → `close`. Then `action_source` is "observed". If
  maintainers did nothing, decide what a careful triager should have done
  from the cutoff facts, and set `action_source` to "inferred". Use `none`
  only when no triager decision was needed at all.
- `decision`:
  - `NOTHING` only when posting would help no one: the comment brings
    nothing a maintainer needs to see, or the PR is already in the hands of
    an assigned maintainer who is actively reviewing it (assigned before
    the comment) and who will see the comment on GitHub anyway.
  - `CARD` only when the PR changed so much since the first look that a
    card written then would now mislead: a different approach, a different
    issue, or most of its files or commits replaced. Rebasing, squashing,
    or fixing what was asked is not enough.
  - `NOTE` otherwise.
- `changed` and `still_missing`: only what the cutoff facts show. Check the
  feedback's asks against the code changes, the description and the
  comment. "Done" with no new push is not a code change. Leave a list empty
  if there is nothing to put in it. Use the later facts only to understand
  what maintainers cared about.
- `must_have`: 2-5 items. Each `fact` is one checkable sentence a good
  note must contain or get right, for example "says the screenshots asked
  for are still missing" or "names timabbott as the reviewer".
  `decisive` is true when missing it alone would change the triager's
  action. `at_cutoff` is true only if the fact is in the cutoff facts.
  Prefer facts that drive the decision (an ask that is still not done,
  failing CI caused by the change, the "help wanted" rule, who should
  review) over descriptive ones.
