You are judging the FACTS in outputs written by a triage bot for the Zulip
open-source project. A triager labeled a contributor's pull request "not
ready" and gave feedback. The PR's author then commented, asking for another
look. The bot took a "second look" and wrote a short note.

Judge only two things in each output: what it says the author did since the
feedback ("new"), and what it says is still missing. Ignore any verdict,
next step, recommended action or reply: those are out of scope here, and
having them or not must not change the score.

Several outputs for the SAME case are labeled with random letters, in random
order; the order carries no information.

What the bot saw (the PR as of the author's comment; its "Second look"
section has the feedback, the code changes since then, and the comment):
<cutoff_facts>{cutoff_facts}</cutoff_facts>

Everything about the PR up to now, including what happened later:
<all_facts>{all_facts}</all_facts>

The key facts, prepared in advance:
<key>{key}</key>

The outputs:
<outputs>{outputs}</outputs>

Use only these inputs. Use the key's `changed` and `still_missing` lists as
given. Facts marked `at_cutoff: false` happened after the author's comment;
no output loses points for missing them.

For each output:
- `wrong_facts`: list every false statement about what changed or what is
  missing, including claiming a requested change was made when the key says
  it is still missing, and the reverse.
- `missed`: key `still_missing` items that matter and that the output leaves
  out.
- `facts_score` from 1 to 10:
  - 9-10: what changed and what is missing are both right and complete for
    the items that matter; no wrong facts
  - 7-8: right, but leaves out one item that matters, or one minor wrong fact
  - 5-6: partly right: misses the main missing item, or one wrong fact that
    matters
  - 3-4: mostly wrong: says done when the main item is still missing, or
    the reverse
  - 1-2: wrong throughout, or a NOTHING/CARD where the key needs a note

Reply with JSON only:
{"outputs": {"<letter>": {"wrong_facts": [...], "missed": [...], "facts_score": <1-10>, "why": "<one sentence>"}}}
