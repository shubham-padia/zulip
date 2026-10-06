# Visual check: claude/botserverrc-docs

Screenshots of the help center dev server (`astro dev`, 1280px wide).
`-old` is `main`, `-new` is this branch.

- `help-manage-a-bot-botserverrc-*`: the new "Download `botserverrc`
  configuration file" section on /help/manage-a-bot. (`-old` shows the
  top of the page, because the section doesn't exist on `main`.)
- `help-deploying-bots-*`: step 2 of "Running multiple bots using the
  Zulip Botserver" on /help/deploying-bots, now linking to the new
  section.

Result: both pages render correctly in light and dark themes. The new
section appears in the "On this page" sidebar, the deploying-bots
step renders as a link to it, and the download icon renders inline. No
problems found.
