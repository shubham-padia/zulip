# Review: `claude/unsubscribed-participants-italic`

Reviewed against `origin/main`, one commit at a time:

1. `09f7202` buddy_list: Remove deactivated users from the buddy list live.
2. `50a64a3` buddy_list: Italicize unsubscribed participants in "This conversation".

## What the branch set out to do

Sources: the request and final report from session
`session_01C3vPqB57toWiPQeyq5RAah`, plus the chat.zulip.org thread
[#feedback > Hide Users in Sidebar if they no longer have channel rights](https://chat.zulip.org/#narrow/channel/137-feedback/topic/Hide.20Users.20in.20Sidebar.20if.20they.20no.20longer.20have.20channel.20rights/with/2428042).

- **Main fix:** keep showing participants who aren't subscribed in "This
  conversation", but in *italics*, with a tooltip that says they aren't
  subscribed. Alya proposed this and Tim endorsed it. A visible
  "(unsubscribed)" label was rejected because it takes too much space.
  The italics must update live when someone subscribes or unsubscribes.
- **Optional extra, as a separate commit:** fix the glitch Alya reported where
  deactivated users briefly show up under "Others".

Both are implemented, each in its own commit.

## Verdict

**No blocking issues.** I found no correctness bugs in either commit. Both
commits do what they claim, and I confirmed the claims in the commit messages
against the code (details below). The remaining points are optional: one
help-center wording fix, plus some test and structure nits.

As instructed, I did not re-run lint or tests, since CI covers them.

---

## Commit 1: `09f7202` Remove deactivated users from the buddy list live

### What it changes

When a `realm_user` update deactivates or reactivates someone,
`user_events.update_person` now calls `activity_ui.redraw_user(user_id)`
instead of `buddy_list.insert_or_move([user_id])`. `redraw_user` now calls
`buddy_list.maybe_remove_user_id` when the user no longer passes
`buddy_data.matches_filter`, where it used to just return.

### Correctness: OK

- **Root cause is right.** `send_events_for_user_deactivation` in
  `zerver/actions/users.py` sends `peer_remove` before the
  `realm_user`/`update` event with `is_active=False`.
  - `peer_remove` leads to `process_subscriber_update`, which runs
    `build_user_sidebar`. At that point the user is still active and no
    longer subscribed, so they land in "Others".
  - The old unconditional `insert_or_move` then put them back in "Others".
  - The new path removes them, because `filter_user_ids` rejects inactive
    non-DM users.
- **Safe for the existing caller (`update_presence_info`).**
  `maybe_remove_user_id` returns early for users who aren't in the list. A
  user who fails `matches_filter` either isn't in the list or (when muted,
  deactivated or deleted) shouldn't be.
- **Other behavior changes from routing through `redraw_user` are fine:**
  - `realm_presence_disabled`: `build_user_sidebar` also bails in that case,
    so there's no buddy list to update.
  - User card open: the redraw is deferred and becomes a full `redraw()` when
    the card closes, which is correct.
  - Deactivated user in a DM narrow with them: `matches_filter` still passes
    (`is_dm`), so they're kept, which matches the full-rebuild behavior.
  - Reactivation: the user passes the filter and is inserted as before.
    `update_indicators()` now also runs, which is harmless.

### Code quality / commit discipline

- The change is minimal and the commit is coherent and stands alone. The
  commit message explains the cause well and the Discussion link points at
  Alya's report.
- The new comment in `redraw_user` explains *why*, which fits the codebase's
  style.
- The commit would also work as its own PR (AGENTS.md: "Open independently
  useful fixes as separate PRs"). The request explicitly asked for a separate
  commit on this branch, so this is only something to consider when opening
  the PR.

### Optional nits

- **Test gap in `user_events.test.cjs`:** `redraw_user` is mocked as a
  no-op, and nothing asserts that it's called with `event.user_id` on
  (de)activation. If someone removed that call, the tests would still pass.
  A small `override` with an assertion in the existing deactivate/reactivate
  block would catch that.
- **Test cleanup:** the new `redraw_deactivated_user` test in
  `activity.test.cjs` restores `mark` with `people.add_active_user` only
  after its assertion passes. If the assertion fails, the state leaks into
  later tests. This is low impact, because a failure there already means a
  red run.

---

## Commit 2: `50a64a3` Italicize unsubscribed participants in "This conversation"

### What it changes

- New `buddy_data.is_unsubscribed_participant(user_id, conversation_participants)`.
  It returns true only for a participant in a channel view where we have
  **full** subscriber data and the user isn't subscribed.
- `info_for` and `get_items_for_users` pass the participants set and add
  `is_unsubscribed_participant` to `BuddyUserInfo`.
- `presence_row.hbs` adds an `unsubscribed-participant` class, and
  `right_sidebar.css` italicizes `.user-name` under it.
- The buddy list tooltip adds an italic line, "Not subscribed to this
  channel.", computed in `click_handlers.ts`.
- `populate()` starts a background
  `rerender_unsubscribed_participants_after_fetching_subscribers()`. For
  channels where we only have partial subscriber data, it waits for the full
  subscriber list and then re-renders the rendered participants who turn out
  to be unsubscribed.
- Help center: `user-list.mdx` gets a sentence about the italics.

### Correctness: OK

I checked each scenario a reader might worry about:

| Scenario | How it's handled | Result |
|---|---|---|
| Another user subscribes or unsubscribes while you view the topic | `peer_add`/`peer_remove` → `process_subscriber_update` → `build_user_sidebar` (full rebuild) | ✅ |
| **You** subscribe or unsubscribe while viewing the topic | `mark_subscribed`/`mark_unsubscribed` both call `build_user_sidebar` | ✅ |
| A new participant posts a message | `rerender_participants` → `insert_or_move` → `get_items_for_users` recomputes the flag | ✅ |
| Large channel, partial subscriber data | Nobody is italicized until `has_full_subscriber_data`, then the rendered participants are re-rendered. Participants rendered later by `render_more` use the full data. | ✅ |
| Narrow changes during the fetch | The `current_sub` identity check skips the update after leaving the channel. For another topic in the same channel, the code reads `participants_section.user_ids` and the participants callback fresh after the `await`, so it acts on the current view. A repeat run is idempotent. | ✅ |
| Fetch fails | `has_full_subscriber_data` stays false, so nothing changes | ✅ |
| Network cost | No new request: `update_section_header_counts` → `non_participant_users_matching_view_count` → `maybe_fetch_is_user_subscribed` already fetches the full list on populate, and `fetch_stream_subscribers` reuses the pending promise | ✅ |
| Bots | Bots never appear in the buddy list (`filter_user_ids`), so integration bots that post without subscribing aren't italicized | ✅ |
| Tooltip and italics consistency | Both use the same `is_unsubscribed_participant` predicate against the same live data | ✅ |
| DM or channel (non-topic) views | The participants set is empty, so the flag is false | ✅ |

All `info_for` callers were updated. `get_items_for_users` is only used by
the buddy list.

### Visual check (cheap approximation)

There's no provisioned dev server, and the author also didn't check the
change in a browser. To check their concern that the slant of the last letter
might get clipped by `.user-name`'s `overflow: hidden`, I rendered one
screenshot in headless Chromium:

- **Setup:** the real Source Sans 3 VF fonts (Zulip's `source-sans-3VF.css`
  includes a true italic face, so the browser doesn't fake the slant), and
  the same `.user-name` box rules: `display: inline-block`,
  `max-width: calc(100% - …)`, `overflow-x: hidden`,
  `text-overflow: ellipsis`.
- **Result:** italic names, including ones ending in descender or overhang
  letters ("Wonderly", "Driftwood"), weren't visibly clipped, and truncated
  names show the ellipsis normally.

This is not a full UI check. It doesn't cover the dark theme, the three
user-list styles in the real app, or the tooltip layout. Someone should still
look at those in the dev server before opening a PR (see
`.claude/rules/ui-testing.md`).

### Findings

1. **Help center and commit message wording is slightly inaccurate (low, worth fixing).**
   - `user-list.mdx` says "Participants who are **no longer** subscribed to
     the channel are shown in *italics*." The commit message also talks about
     "past participants … no longer subscribed".
   - The code italicizes *any* participant who isn't currently subscribed.
     That includes people who were never subscribed, e.g. someone who posted
     in a public channel they never joined, which Zulip allows.
   - The tooltip ("Not subscribed to this channel.") is accurate. The help
     center should match it, e.g. "Participants who aren't subscribed to the
     channel are shown in *italics*."
2. **Structure nit (optional): the tooltip data is assembled in `click_handlers.ts`.**
   - `TitleData` gains an optional `is_unsubscribed_participant`, but
     `get_title_data` never sets it. Instead, the buddy-list hover handler
     spreads `get_title_data(...)` and adds the field, calling
     `get_conversation_participants_callback()()` itself.
   - This works, and it keeps `get_title_data` free of narrow logic for the
     DM-list tooltip caller (which passes `is_group`). But this setup means
     only one of the two `get_title_data` callers can ever set the flag.
   - A reviewer may prefer setting the field inside `get_title_data` for the
     single-user case, or a small helper in `buddy_data`.
3. **Structure nit (optional): a second background task alongside an existing await.**
   - `populate()` now starts `rerender_unsubscribed_participants_after_fetching_subscribers`
     next to `render_view_user_list_links` and `update_empty_list_placeholders`.
     Meanwhile `update_section_header_counts` already awaits the same full
     fetch.
   - Keeping them separate is reasonable for readability, and the promise is
     shared, so there's no extra request. I'm mentioning it only so the
     choice is deliberate.
4. **Design point to confirm (raised by the author, not a bug): guests.**
   - `user_full_name.hbs` renders the guest indicator as
     `<i class="guest-indicator">(guest)</i>`.
   - For an unsubscribed guest participant, the whole row is now italic, so
     the "(guest)" suffix no longer stands out against the name.
   - This is rare and probably fine. It fits with the author's open
     questions about tooltip wording and placement (the new line goes directly
     under the name, above the status and last-seen lines) and about
     italicizing yourself. The author listed all of these in the report, so
     they should go to the reviewers in the PR description, not be decided
     silently.

### Tests

- `buddy_data.test.cjs` covers:
  - outside a channel view;
  - a subscribed participant, an unsubscribed participant, and a
    non-participant;
  - partial subscriber data;
  - the `get_items_for_users` integration.
- `buddy_list.test.cjs` covers the async re-render: rerendering after the
  fetch, no refetch once the data is full, nothing to rerender, a narrow
  change during the fetch, and no channel view. It uses the established
  `mock_channel_get` helper.
- These cover the new branches well.
- The new `buddy_data` tests call `message_lists.set_current(...)` without
  resetting it at the end, unlike the `buddy_list` test. This only matters if
  later tests in that file depend on `message_lists.current` being undefined.
  CI passes, so it's only a tidiness nit.

### Commit discipline

- The commit is coherent and includes its tests.
- The changes to existing expectations (`is_unsubscribed_participant: false`
  in `activity.test.cjs` and `buddy_data.test.cjs`) belong in this commit, and
  the author correctly kept them out of commit 1.
- The commit message explains the partial-data strategy and the live-update
  path, which I confirmed against the code above. It also records the rejected
  "(unsubscribed)" label alternative.
- The commit doesn't depend on commit 1, and commit 1 doesn't depend on it.

---

## Is anything left unfixed?

No. Both items from the request are implemented:

- The italic name plus tooltip, including live updates and correct handling
  of large channels.
- The deactivation glitch, as a separate commit.

The only remaining gap is process, not code: the author never checked the
change visually in the real app. Before a PR, check it in all three
user-list styles and both themes, and check the tooltip, per
`.claude/rules/ui-testing.md`.
