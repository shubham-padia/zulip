# Review: `claude/deleted-topic-sidebar-compose`

Reviewed against `origin/main`, one commit at a time:

1. `a3b4b77` left_sidebar: Stop showing the viewed topic after it's deleted.
2. `0c46ddd` compose: Close an empty compose box when its topic is deleted.

## What the branch set out to do

These sources define the goal:

- **The request to the authoring session** (`session_01XhwNHkpbU1BUScXxMYGEed`). When a user deletes the topic they are viewing:
  - The topic should leave the left sidebar right away, for the user who deleted it and ideally for other clients too.
  - An empty compose box addressed to the topic should close. A box with a typed draft should stay open.
  - The request also said not to redirect to the channel feed, and to list that as an open question.
- **The chat.zulip.org thread** "Left sidebar not resetting after active topic deletion" (#issues):
  - The reporter's three expectations were: clear the compose box, remove the topic from the sidebar, and redirect.
  - Evy (core dev) endorsed only the first two. She asked for an empty compose box to close and a box with a draft to stay open.
  - The thread links zulip/zulip#11665.

**Verdict:** Both agreed behaviors are implemented. The redirect is correctly left as an open question. I found no correctness bugs that block merging. Below are one behavior caveat worth a maintainer's attention, plus a few test and naming nits.

## Root cause check

The diagnosis in commit 1 is correct:

- When the last locally known message of a topic is deleted, `stream_topic_history.remove_messages` drops the topic through `PerStreamHistory.maybe_remove`. It then asks the server whether the topic still has messages (`update_topic_last_message_id` → `message_util.get_last_message_id_in_narrow`). The server callback only re-adds the topic if a message still exists.
- `topic_list_data.get_filtered_topic_names` then unconditionally adds `narrow_state.topic()` back, through the "viewing a topic with no messages" `unshift`. That is why the topic disappeared once the reporter clicked away.
- The existing `stream_list.update_streams_sidebar()` call in the `delete_message` handler already re-renders the zoomed topic list, through `update_stream_sidebar_for_narrow`. So once the force-add is suppressed, the sidebar updates live.

## Commit 1: `a3b4b77` left_sidebar: Stop showing the viewed topic after it's deleted.

### Approach

- When a `delete_message` event leaves the topic with no local history, `topic_list_data.handle_deleted_topic` records it in the module state `deleted_narrowed_topic`, but only if it is the narrowed topic.
- `get_filtered_topic_names` skips the force-add for that topic.
- `stream_list.handle_narrow_activated` clears the state. That function is called from both `message_view.show` and the inbox channel view.

### Correctness

I traced these cases and they all behave correctly:

- **Batched deletes of large topics.** `message_delete.delete_topic` retries and the server deletes in batches. An intermediate batch can empty the local count. The server re-fetch then re-adds the topic, so `contains_topic` is true and it shows normally. The final batch removes it again, and the flag is still set, so it stays hidden. The persistent flag handles this better than a one-shot check would.
- **Messages later sent or moved into the topic.** The topic is back in history, `contains_topic` is true, and it shows normally (tested).
- **Leaving for a non-narrow view (Inbox, Recent) and coming back.** `narrow_state.topic()` is `undefined` in those views, so the stale flag has no effect. Any narrow back to the topic clears it.
- **Case-insensitive matching.** Both comparisons use `util.lower_same`, consistent with `contains_topic` and the case-insensitive `FoldDict` in topic history.
- **Other clients viewing the topic.** They take the same dispatch path, so they get the fix too, as requested.

### Code structure and quality

- The change is small and well placed. The state lives next to the only code that reads it, and the new comment on the `unshift` explains the exception.
- **Naming nit.** `topic_list_data.handle_deleted_topic` sounds general but only records the narrowed topic. Commit 2's counterpart is named `compose_actions.on_topic_deleted`. Two hooks called side by side from the same `if` block use different naming patterns. Matching names, or a more specific one such as `handle_narrowed_topic_deleted`, would read better in `server_events_dispatch.js`.

### Tests

- **Nit in `topic_list_data.test.cjs`.** The first block calls `stream_topic_history.remove_messages` for "deleted topic". Then `delete_topic_messages("deleted topic")` calls it again, and the second call is a no-op because the topic is already gone. The test is correct, but a reader has to work out that only the `handle_deleted_topic` call matters there.
- **`dispatch.test.cjs`: the "topic still has other messages" case asserts nothing about the hook.** It installs `handle_deleted_topic` as `noop` with `{unused: false}`, which accepts the hook being called or not. Only the second dispatch, which asserts `num_calls === 1`, checks the condition. A regression that dropped the `if` and always called the hook would still pass. A stub that throws, or `make_stub()` plus `assert.equal(stub.num_calls, 0)`, would cover that branch. Commit 2 copies the same pattern for `on_topic_deleted`.

### Commit message

- The message follows the repo format and explains the cause, the fix, and why clearing on narrow is right.
- It links the chat.zulip.org discussion and omits "Fixes #11665". The authoring session said it did that because it hadn't confirmed the issue matches exactly. That is a reasonable choice, but the PR description should mention #11665.

## Commit 2: `0c46ddd` compose: Close an empty compose box when its topic is deleted.

### Approach

- `compose_actions.on_topic_deleted` is called from the same "topic no longer in local history" branch.
- It does nothing unless the compose box is a channel message to that channel and topic (case-insensitive).
- It leaves the box open if `compose_state.has_message_content()` is true, and otherwise calls `cancel()`.
- This applies whether or not the user is viewing the topic. That follows the reasoning in the thread: the risk is sending to the deleted topic, not viewing it.

### Correctness

- A closed compose box has `get_message_type() === undefined` and returns early (tested).
- DM compose returns early (tested).
- An unselected channel (`""`) never equals a numeric `stream_id` (tested).
- A typed draft is preserved (tested). That is the key requirement from Evy.

### Behavior caveat (applies to both commits, matters most here)

Both hooks fire whenever the topic is missing from local `stream_topic_history` after `remove_messages`. Local history is approximate:

- `TopicHistoryEntry.count` counts only locally known messages.
- Topics learned from server history have `count: 0`.
- `maybe_remove` drops a topic as soon as an event deletes at least `count` messages, and asks the server later.
- `channel_has_locally_available_topic` is also false for topics that were never in local history.

So both hooks can fire for a topic that still has messages on the server. Two examples:

- **The topic is known only from server history.** A user has an empty compose box addressed to a topic whose messages they haven't loaded. Someone else deletes one message in that topic. The user's compose box closes.
- **An API bulk delete in a large topic.** A user views the newest messages of a large topic with an empty compose box open. A bulk delete through the API removes more old, unloaded messages than the client has loaded. The compose box closes. The sidebar entry also disappears until the server re-fetch returns. On `main` the sidebar entry would not flicker, because the force-add kept it.

**Impact:**

- **Sidebar:** the server re-fetch fixes it on its own.
- **Compose:** the box stays closed. Nothing is lost because it was empty, and normal UI deletions of single loaded messages don't hit this case.

**Options:**

- Accept the caveat, as the authoring session did. It listed this in its final report.
- Act only once the server confirms the topic is gone. This would need the "no messages" outcome of `update_topic_last_message_id`, which today only has a success-with-message callback. It is a larger change.

The PR description should say which option was chosen.

### Code structure and quality

- The function is small and readable, and the early-return guards match the style of nearby `compose_actions` functions.
- The comments say why ("so that the user doesn't accidentally recreate the deleted topic"), not what.

### Tests

- The `on_topic_deleted` unit test covers each guard.
- **Readability nit.** The helper `compose_to(stream_id, ...)` shadows the outer `const stream_id`. Renaming either one would avoid that.
- The `dispatch.test.cjs` gap described under commit 1 applies here too.

### Commit message

The message is clear. It states the draft-preservation rule and that the behavior applies on every client and whether or not the user is viewing the topic.

## Commit discipline

- **Separable changes.** Each commit is one coherent change. Commit 1 adds the dispatch branch and commit 2 adds one call inside it. Neither commit moves code while changing it.
- **Independence.** Commit 1 works and passes on its own, and commit 2 can be dropped without breaking commit 1.
- **Fixups.** Neither commit fixes up the other.

## Requirements checklist

| Requirement | Status |
| --- | --- |
| Deleted active topic leaves the left sidebar immediately | Done (commit 1) |
| For other clients receiving the events too | Done (same dispatch path) |
| Empty compose box closes | Done (commit 2) |
| Compose box with a draft stays open | Done (commit 2) |
| Don't redirect to the channel feed; raise it as an open question | Done (listed in the authoring session's report) |
| Node tests for the new behavior | Done. See the `dispatch.test.cjs` nit about the negative case |

## Verification notes

- I traced the code paths above by reading the code. I read the `stream_topic_history`, `stream_topic_history_util`, `message_util`, `message_delete`, `stream_list` and `compose_state` code involved.
- Per instructions, I did not re-run lint or tests, because CI covers them.
- I did not do a browser check. The authoring session couldn't run `./tools/provision` in its container. The sidebar re-render relies on the existing `update_streams_sidebar` → `update_stream_sidebar_for_narrow` path, which already runs on this event. A quick manual check in the dev server is still worth doing before opening a PR: delete the viewed topic with an empty compose box, then with a draft.

## Summary of findings

1. **Behavior caveat (minor, needs a decision):** both hooks can fire for a topic that still has messages on the server, because local topic history is approximate. The sidebar fixes itself after the server re-fetch. An empty compose box can be closed when it shouldn't be. Accept and document it, or act only after the server confirms.
2. **Test gap (nit):** the "topic still has other messages" case in `dispatch.test.cjs` doesn't assert that the hooks are not called.
3. **Naming nit:** `handle_deleted_topic` and `on_topic_deleted` are named inconsistently, and the first name is broader than what the function does.
4. **Test readability nits:** the topic_list_data test calls `remove_messages` twice for the same topic, and `compose_to` shadows `stream_id` in the compose test.
