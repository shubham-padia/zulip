# Review: `claude/botserverrc-docs` against `origin/main`

**Commit reviewed:** `afc6cf3` help: Document where to download the botserverrc file.

**Files:** `starlight_help/src/content/docs/manage-a-bot.mdx`,
`starlight_help/src/content/docs/deploying-bots.mdx` (+16 / −10)

**Verdict:** Ready to go. There are no blocking findings, and the commit
does what the chat thread agreed on. Two optional nits are listed below.

## What the fix set out to do

From the chat.zulip.org thread
([#issues > option to download `botserverrc` file missing](https://chat.zulip.org/#narrow/channel/9-issues/topic/option.20to.20download.20.60botserverrc.60.20file.20missing/with/2529990))
and the original session's task:

- A user, following `/help/deploying-bots`, couldn't find the `botserverrc`
  download button in either Personal settings or Organization settings.
- Sahil Batra confirmed that the button appears only on the **Your bots** tab,
  and only if the user owns at least one active **outgoing webhook** bot. He
  agreed that "we should update the documentation to make this clear."
- Showing the button on the **All bots** tab was suggested but not agreed. It
  was correctly left out of scope, and the session's final report mentions it.

## Checking the claims against the code

| Claim in the new docs | Source | OK? |
|---|---|---|
| Button is on the **Your bots** tab | `web/templates/settings/bot_list_admin.hbs`: `.config-download-text` is inside `#{{prefix}}-your-bots-list` only | ✅ |
| Only shown if the user owns ≥1 *active* outgoing webhook bot | `toggle_bot_config_download_container()` in `web/src/settings_bots.ts` filters `get_all_bots_for_current_user()` by `OUTGOING_WEBHOOK_BOT_TYPE_INT` and `is_person_active` | ✅ |
| File covers all of the user's active outgoing webhook bots | Same filter, plus the template text "Download config of all active outgoing webhook bots in Zulip Botserver format." | ✅ |
| It's a **download** icon above the bots table | `icon_button icon="download"`, rendered before `bot_list` in the same section | ✅ |
| `<NavigationSteps target="settings/your-bots" />` is valid | `"your-bots"` entry in `starlight_help/src/components/SettingsSteps.astro`, and used elsewhere on the same page | ✅ |

**Is "Select the Your bots tab" redundant?** No. `#settings/your-bots` lands on
that tab, but `SettingsPanelMenu.set_bot_settings_tab` remembers the last
selected bot tab for the session. A user who earlier clicked **All bots**
returns to **All bots** when they reopen Personal settings → Bots. That is the
exact trap from the thread, so the explicit step is needed. Its wording matches
existing help center usage (e.g., "Select the **Invitations** tab." in
`invite-new-users.mdx`).

## Code structure and quality

- The new `## Download \`botserverrc\` configuration file` section mirrors the
  existing `## Download \`zuliprc\` configuration file` section on the same
  page: an H2, an intro paragraph, then `FlattenedSteps` + `NavigationSteps`.
  `deploying-bots.mdx` now links to the new anchor, just as its `zuliprc` step
  already does. This fits the page well.
- The anchor `#download-botserverrc-configuration-file` follows the same slug
  pattern as the existing, working `#download-zuliprc-configuration-file`.
- Imports are correct:
  - `DownloadIcon` was removed from `deploying-bots.mdx`, where it is no longer
    used.
  - `manage-a-bot.mdx` still uses `ZulipTip` (in the API key section) and
    `DownloadIcon`, so those imports must stay, and they do.
- No other help center, `docs/` or `api_docs/` page mentions `botserverrc`, so
  no other page needed updating.

## Commit discipline

- One coherent change, in a single commit. The subsystem prefix `help:` is
  right.
- The commit message explains the user-facing problem, both visibility
  conditions and the approach, and links the discussion. The body is wrapped
  correctly; only the URL line is long, which the commit-message guide allows.
- No unrelated changes. The UI was not touched, which is correct.

## Findings

### Blocking

None.

### Optional (nits)

1. **The conditions are written in two places.** The `deploying-bots.mdx`
   step repeats "shown on the **Your bots** tab, and only if you own at least
   one active **outgoing webhook** bot", and the linked section says the same
   thing. If the UI changes (for example, the "All bots" follow-up), both
   places need editing.
   - The repetition is defensible, since `deploying-bots` is where the reporter
     got stuck.
   - Trimming it to just the link, like the neighbouring `zuliprc` step, would
     also be fine.
   - Either choice is acceptable.

2. **The Organization settings path isn't mentioned.** The same button also
   appears on the **Your bots** tab of Organization settings → Bots (`admin`
   prefix of the same template). There, the tab defaults to **All bots**,
   which is likely why the reporter missed it.
   - The docs give one working path (Personal settings), which is enough for
     this fix.
   - This is noted only for completeness, not as a requested change.

## Visual check

Screenshots of the help center dev server (1280px wide) are in
`screenshots/`, with notes in `screenshots/README.md`. They were taken in
another session; I looked at all four "after" (`-new`) screenshots myself.

- **Both pages render correctly in light and dark themes.** Text, code
  formatting, links and step numbers look right, with no layout problems.
- **The new section appears in "On this page".** On `/help/manage-a-bot`,
  "Download botserverrc configuration file" is listed between "Download
  zuliprc configuration file" and "Get a bot's API key".
- **The section reads as intended.** Its three steps render as "Navigate to
  the **Bots** tab of the **Personal settings** menu", "Select the **Your
  bots** tab", and "Click the **download** icon above the bots table". The
  download icon renders inline in both themes.
- **The deploying-bots step links to the new section.** On
  `/help/deploying-bots`, step 2 of "Running multiple bots using the Zulip
  Botserver" renders "Download the `botserverrc` file" as a link, followed by
  the two visibility conditions.

## What was and wasn't checked

- I didn't rerun lint or the help build, because CI covers them, as
  instructed.
- I checked the doc claims against the template and TypeScript source above.
  The rendering was checked using the screenshots in the "Visual check"
  section.
- Context came from the original session's transcript (user and assistant
  messages) and from the linked chat.zulip.org thread.

## Commit message reword

The fix commit's message was reworded using the newer commit-message
guide on the `commit-message-skill` branch. Only the message changed:
`git diff e28c04813e 2cceb26a7c` prints nothing. Author and committer
are both `Shubham Padia <shubham@zulip.com>`, and Claude appears only
as the `Co-Authored-By` trailer.

What changed, per the guide:

- **The summary names the problem, not the fix.**
- **The body is shorter.** It drops the sentence that described the diff
  (replacing the tip and adding the link) and keeps why the approach is
  right (it mirrors the `zuliprc` docs).
- **The body is wrapped at 70 characters or fewer.**

**Status:** `2cceb26a7c` exists locally as branch
`reworded-botserverrc-docs`, but it has **not** been pushed.
`claude/botserverrc-docs` still points at `e28c04813e`, because the
force-push was blocked by this session's permission settings.

### Old message (`e28c04813e`)

```
help: Document where to download the botserverrc file.

The "Deploying bots in production" article told users to download
the botserverrc file using a download icon above the bots table, but
that icon only appears on the "Your bots" tab, and only when the user
owns at least one active outgoing webhook bot, since the file only
contains configuration for those bots. Users who didn't meet both
conditions couldn't find the button.

Replace the tip in "Manage a bot" with a dedicated section that
explains these conditions and gives navigation steps, and link to it
from the Botserver instructions, mirroring how the zuliprc download
is documented.

Discussion: https://chat.zulip.org/#narrow/channel/9-issues/topic/option.20to.20download.20.60botserverrc.60.20file.20missing/with/2529990

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

### New message (`2cceb26a7c`)

```
help: Fix botserverrc download steps omitting when the icon shows.

The "Deploying bots in production" article said to download the
botserverrc file from a download icon above the bots table. That
icon only appears on the "Your bots" tab, and only if the user owns
an active outgoing webhook bot. Users missing either condition
couldn't find it.

The new "Manage a bot" section states both conditions, mirroring
how the zuliprc download is documented.

Discussion: https://chat.zulip.org/#narrow/channel/9-issues/topic/option.20to.20download.20.60botserverrc.60.20file.20missing/with/2529990

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```
