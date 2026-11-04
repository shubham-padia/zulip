You are judging outputs written by a triage bot for the Zulip open-source
project. A triager labeled a contributor's pull request "not ready" and gave
feedback. The PR's author then commented, asking for another look. The bot
took a "second look" and wrote one of:
- NOTHING: nothing is posted, because no maintainer needs to see this.
- NOTE: a short note under the PR's first card in the maintainers' Zulip
  topic: what changed, what's still missing, the next step, and a reply to
  paste on GitHub.
- CARD: a full new card about the PR, because the PR changed so much that
  the first card would mislead.
The triager reading it decides to hand the PR off for review (remove "not
ready", add "maintainer review", assign a reviewer), give more feedback, or
close it.

Several outputs for the SAME case were written by different prompts or
runs. They are labeled with random letters and shown in random order; the
order carries no information.

What the bot saw (the PR as of the author's comment; its "Second look"
section has the feedback, the code changes since then, and the comment):
<cutoff_facts>{cutoff_facts}</cutoff_facts>

Everything about the PR up to now, including what happened later:
<all_facts>{all_facts}</all_facts>

The key facts, prepared in advance:
<key>{key}</key>

The outputs:
<outputs>{outputs}</outputs>

Use only these inputs. Use the key as given; don't re-derive it. Facts
marked `at_cutoff: false` happened after the author's comment. They may
explain the maintainers' decision, but no output loses points for missing
them.

Step 1: check each output.
- `kind`: its first line, NOTHING, NOTE or CARD.
- `action`: the triager action it recommends, from its verdict and next
  step: hand_off, more_feedback, close, or none (for NOTHING).
- Mark every `must_have` id present, missing, hedged, or wrong.
- List wrong facts: false statements, even plausible guesses. Saying a
  requested change was made when the key says it is still missing is a
  wrong fact, and so is the reverse.
- List rule failures, in snake_case: for example `reply_contradicts_verdict`,
  `names_contributor`, `code_details`, `filler_point`, `soft_closing_reply`,
  `asks_for_done_work`, `bad_format`.

Step 2: score each output from 1 to 10.
decision_score (was NOTHING/NOTE/CARD and the action the right call):
- 9-10: kind and action both match the key
- 7-8: action matches; kind is NOTE where the key says CARD or the reverse
- 5-6: kind matches, and the action is a defensible near miss of an
  inferred key action
- 3-4: wrong action (for example hand_off where the key says more_feedback)
- 1-2: NOTHING where the key needs a triager decision, or hand_off or
  more_feedback where the key says close, or the reverse
accuracy_score (what changed and what's still missing):
- 9-10: every `changed` and `still_missing` item that matters is right,
  every cutoff must-have present, no wrong facts
- 7-8: one non-decisive item missing or vague
- 5-6: a decisive must-have missing, or two or more items missing
- 3-4: a wrong fact the action rests on
- 1-2: mostly wrong
reply_score:
- 9-10: a maintainer would paste it as is
- 7-8: paste after changing a word or two
- 5-6: right ask, but the tone or a missing reference means rewriting a
  sentence
- 3-4: wrong ask, or misses `reply_ask`
- 1-2: wrong decision, such as telling an author whose PR should be
  closed to keep going, or asking for work that is already done
When the key's action is hand_off, "No reply needed." or a single reviewer
ping line scores 9-10, and a reply of two or more sentences to the author
scores at most 6.
brevity_score:
- 9-10: nothing to cut; it doesn't restate what the triager already knows
- 7-8: one line or point could go
- 5-6: several lines could go, or it repeats the first card
- 3-4: about twice as long as needed
- 1-2: much longer than needed
For a NOTHING output: if the key's decision is NOTHING, every score is 10.
Otherwise decision_score is 1-2, accuracy_score and reply_score are 1, and
brevity_score is null. For a NOTE or CARD where the key says NOTHING, score
decision_score 3-4 and the other parts as written.

Adjustments: a wrong fact that the action or the reply's ask rests on caps
accuracy_score and reply_score at 4. Any other wrong fact subtracts 2 from
accuracy_score. Each rule failure subtracts 1 from the part it affects.
Then look at the outputs that share a score, and if two aren't
interchangeable, adjust one. Make at most 3 such adjustments.

Step 3: rank all outputs, best first, by how useful they are to the
triager. Break ties by fewer wrong facts, then fewer words.

Reply with only this JSON, with one sentence for each "why":
{"outputs": {"<letter>": {"kind": "NOTE", "action": "more_feedback",
   "facts": {"<id>": "present|missing|hedged|wrong"},
   "wrong_facts": ["..."], "rule_failures": ["..."],
   "decision_score": 8, "accuracy_score": 7, "reply_score": 7,
   "brevity_score": 8,
   "decision_why": "...", "accuracy_why": "...", "reply_why": "..."}},
 "ranking": ["<best letter>", "..."]}
