# Visual check: claude/unsubscribed-participants-italic

Screenshots from the dev environment (Puppeteer). `-old` is `main`,
`-new` is this branch.

## Commit 2: italicize unsubscribed participants

Setup: Zoe and Polonius (a guest) both posted in #Verona > printer.
Both were unsubscribed from #Verona, then Desdemona viewed the topic.

- `unsub-participants-section-*`: on this branch, both rows under "This
  conversation" are italic; on `main` neither is.
- `unsub-participants-tooltip-*`: on this branch, the tooltip adds
  "Not subscribed to this channel." in italics.
- The italic appeared 0.6–1.0s after opening the topic, across three
  runs. It comes from the background subscriber fetch, so there is a
  brief non-italic flash for channels without full subscriber data.

Guest rows: the whole row is italic, so "Polonius (guest)" no longer
sets the "(guest)" label apart (it is italic on its own on `main`).
This confirms the design question in the review; see
`unsub-participants-section-light-new.png`.

## Commit 1: remove deactivated users from the buddy list live

Setup: "Others" expanded, then Othello (in "This channel") was
deactivated through the API. A DOM observer recorded each time
Othello's row was added to or removed from "Others".

- `main`: added, removed, added. Othello is left under "Others"
  (`deactivate-after-light-old.png`).
- This branch: added, removed. Othello is gone
  (`deactivate-after-light-new.png`).

Minor finding: on this branch the "Others" count goes from 3 to 4
after the deactivation and stays at 4, although Othello isn't listed.
`maybe_remove_user_id` removes the row but doesn't refresh the section
header counts. `other_users_count` comes from the last full rebuild,
which ran on the unsubscribe events while Othello was still active. On
`main` the count is also 4, but there Othello is wrongly listed.
