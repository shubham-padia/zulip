# Visual check: claude/channel-admin-text

Screenshots from the dev environment (Puppeteer, 1400px wide unless
noted). `-old` is `main`, `-new` is this branch.

- `*-settings-*`: channel settings → Permissions → "Administrative
  permissions" for #Verona. `*-tip-*` are zoomed crops of the tip.
- `*-create-*`: the create-channel form, with "Advanced configuration"
  expanded.
- `*-480px-*`: channel settings at 480px wide.

Result: the new sentence and the (?) help link render in both places,
in light and dark themes. The icon sits right after the sentence, and
at 480px the sentence wraps with the icon staying on the last line.
No problems found.
