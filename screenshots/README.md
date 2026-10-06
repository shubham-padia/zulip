# Visual check: claude/deleted-topic-sidebar-compose

Screenshots from the dev environment (Puppeteer). `-old` is `main`,
`-new` is this branch. In each case Desdemona sends a message to a new
topic in #Verona, views it, opens an empty compose box with `r`, and
then deletes the topic through the API.

| Case | `main` | this branch |
| --- | --- | --- |
| Empty compose box (light and dark) | Topic stays in the left sidebar; compose box stays open | Topic leaves the sidebar; compose box closes |
| Compose box with a drafted message | Topic stays; compose stays open | Topic leaves the sidebar; compose stays open with the draft |

Both commits behave as described.

One observation (not a regression): after the compose box closes, the
closed compose bar still reads "Message #Verona > <deleted topic>",
because the user is still viewing that topic. One click reopens
compose to the deleted topic. This matches how Zulip treats any empty
topic you're viewing, but it is relevant to the stated goal of not
accidentally recreating the topic. See
`deleted-topic-empty-compose-after-light-new.png`.
