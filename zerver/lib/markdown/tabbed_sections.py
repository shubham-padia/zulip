import re
from typing import Any, Dict, List, Mapping, Optional

import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from typing_extensions import override

from zerver.lib.markdown.priorities import PREPROCESSOR_PRIORITIES
from zerver.lib.markdown.help_relative_links import RelativeLinks

START_TABBED_SECTION_REGEX = re.compile(r"^\{start_tabs\}$")
END_TABBED_SECTION_REGEX = re.compile(r"^\{end_tabs\}$")
TAB_CONTENT_REGEX = re.compile(r"^\{tab\|([^}]+)\}$")

TABBED_SECTION_TEMPLATE = """
import {{ Tabs, TabItem }} from '@astrojs/starlight/components';

<Tabs>
{blocks}
</Tabs>
""".strip()

NAV_BAR_TEMPLATE = """
<ul class="nav">
{tabs}
</ul>
""".strip()

NAV_LIST_ITEM_TEMPLATE = """
<li data-tab-key="{data_tab_key}" tabindex="0">{label}</li>
""".strip()

DIV_TAB_CONTENT_TEMPLATE = """
<TabItem label="{data_tab_key}">
{content}
</TabItem>
""".strip()

# If adding new entries here, also check if you need to update
# tabbed-instructions.js
TAB_SECTION_LABELS = {
    "desktop-web": "Desktop/Web",
    "ios": "iOS",
    "android": "Android",
    "mac": "macOS",
    "windows": "Windows",
    "linux": "Linux",
    "most-systems": "Most systems",
    "linux-with-apt": "Linux with APT",
    "python": "Python",
    "js": "JavaScript",
    "curl": "curl",
    "zulip-send": "zulip-send",
    "web": "Web",
    "desktop": "Desktop",
    "mobile": "Mobile",
    "mm-default": "Default installation",
    "mm-cloud": "Cloud instance",
    "mm-docker": "Docker",
    "mm-gitlab-omnibus": "GitLab Omnibus",
    "mm-self-hosting-cloud-export": "Self hosting (cloud export)",
    "require-invitations": "Require invitations",
    "allow-anyone-to-join": "Allow anyone to join",
    "restrict-by-email-domain": "Restrict by email domain",
    "zoom": "Zoom",
    "jitsi-meet": "Jitsi Meet",
    "bigbluebutton": "BigBlueButton",
    "disable": "Disabled",
    "chrome": "Chrome",
    "firefox": "Firefox",
    "desktop-app": "Desktop app",
    "system-proxy-settings": "System proxy settings",
    "custom-proxy-settings": "Custom proxy settings",
    "stream": "From a stream view",
    "not-stream": "From other views",
    "via-recent-conversations": "Via recent conversations",
    "via-inbox-view": "Via inbox view",
    "via-left-sidebar": "Via left sidebar",
    "via-right-sidebar": "Via right sidebar",
    "instructions-for-all-platforms": "Instructions for all platforms",
    "public-channels": "Public channels",
    "private-channels": "Private channels",
    "web-public-channels": "Web-public channels",
    "via-user-card": "Via user card",
    "via-user-profile": "Via user profile",
    "via-organization-settings": "Via organization settings",
    "via-personal-settings": "Via personal settings",
    "via-channel-settings": "Via channel settings",
    "default-subdomain": "Default subdomain",
    "custom-subdomain": "Custom subdomain",
    "zulip-cloud-standard": "Zulip Cloud Standard",
    "zulip-cloud-plus": "Zulip Cloud Plus",
    "request-sponsorship": "Request sponsorship",
    "request-education-pricing": "Request education pricing",
    "zulip-cloud": "Zulip Cloud",
    "self-hosting": "Self hosting",
    "okta": "Okta",
    "onelogin": "OneLogin",
    "azuread": "AzureAD",
    "entraid": "Microsoft Entra ID",
    "keycloak": "Keycloak",
    "auth0": "Auth0",
    "logged-in": "If you are logged in",
    "logged-out": "If you are logged out",
    "user": "User",
    "bot": "Bot",
    "on-sign-up": "On sign-up",
    "via-paste": "Via paste",
    "via-drag-and-drop": "Via drag-and-drop",
    "via-markdown": "Via Markdown",
    "via-compose-box-buttons": "Via compose box button",
    "channel-compose": "Compose to a channel",
    "dm-compose": "Compose a DM",
    "v8": "Zulip Server 8.0+",
    "v6": "Zulip Server 6.0+",
    "v4": "Zulip Server 4.0+",
    "all-versions": "All versions",
    "for-a-bot": "For a bot",
    "for-yourself": "For yourself",
}


class TabbedSectionsGenerator(Extension):
    @override
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.preprocessors.register(
            TabbedSectionsPreprocessor(md, self.getConfigs()),
            "tabbed_sections",
            PREPROCESSOR_PRIORITIES["tabbed_sections"],
        )


class TabbedSectionsPreprocessor(Preprocessor):
    def __init__(self, md: markdown.Markdown, config: Mapping[str, Any]) -> None:
        super().__init__(md)

    @override
    def run(self, lines: List[str]) -> List[str]:
        tab_section = self.parse_tabs(lines)
        while tab_section:
            if "tabs" in tab_section:
                tab_class = "has-tabs"
            else:
                tab_class = "no-tabs"
                tab_section["tabs"] = [
                    {
                        "tab_key": "instructions-for-all-platforms",
                        "start": tab_section["start_tabs_index"],
                    }
                ]
            content_blocks = self.generate_content_blocks(tab_section, lines)
            rendered_tabs = TABBED_SECTION_TEMPLATE.format(
                blocks=content_blocks
            )

            start = tab_section["start_tabs_index"]
            end = tab_section["end_tabs_index"] + 1
            lines = [*lines[:start], rendered_tabs, *lines[end:]]
            tab_section = self.parse_tabs(lines)

        return lines

    def generate_content_blocks(self, tab_section: Dict[str, Any], lines: List[str]) -> str:
        tab_content_blocks = []
        for index, tab in enumerate(tab_section["tabs"]):
            start_index = tab["start"] + 1
            try:
                # If there are more tabs, we can use the starting index
                # of the next tab as the ending index of the previous one
                end_index = tab_section["tabs"][index + 1]["start"]
            except IndexError:
                # Otherwise, just use the end of the entire section
                end_index = tab_section["end_tabs_index"]

            content = "\n".join(lines[start_index:end_index]).strip()
            tab_content_block = DIV_TAB_CONTENT_TEMPLATE.format(
                data_tab_key=tab["tab_key"],
                # Wrapping the content in two newlines is necessary here.
                # If we don't do this, the inner Markdown does not get
                # rendered properly.
                content=f"\n{content}\n",
            )
            tab_content_blocks.append(tab_content_block)
        return "\n".join(tab_content_blocks)

    def generate_nav_bar(self, tab_section: Dict[str, Any]) -> str:
        li_elements = []
        for tab in tab_section["tabs"]:
            tab_key = tab.get("tab_key")
            tab_label = TAB_SECTION_LABELS.get(tab_key)
            if tab_label is None:
                raise ValueError(
                    f"Tab '{tab_key}' is not present in TAB_SECTION_LABELS in zerver/lib/markdown/tabbed_sections.py"
                )

            li = NAV_LIST_ITEM_TEMPLATE.format(data_tab_key=tab_key, label=tab_label)
            li_elements.append(li)

        return NAV_BAR_TEMPLATE.format(tabs="\n".join(li_elements))

    def parse_tabs(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        block: Dict[str, Any] = {}
        for index, line in enumerate(lines):
            start_match = START_TABBED_SECTION_REGEX.search(line)
            if start_match:
                block["start_tabs_index"] = index

            tab_content_match = TAB_CONTENT_REGEX.search(line)
            if tab_content_match:
                block.setdefault("tabs", [])
                tab = {"start": index, "tab_key": tab_content_match.group(1)}
                block["tabs"].append(tab)

            end_match = END_TABBED_SECTION_REGEX.search(line)
            if end_match:
                block["end_tabs_index"] = index
                break
        return block


def makeExtension(*args: Any, **kwargs: str) -> TabbedSectionsGenerator:
    return TabbedSectionsGenerator(**kwargs)

from zerver.lib.markdown.tabbed_sections import TabbedSectionsPreprocessor


test_markdown = '''
# View channel subscribers

Who is subscribed to a channel determines who receives the messages sent there.
All non-[guest](/help/guest-users) users can view public channels and subscribe
themselves. Organization administrators can
[configure](/help/configure-who-can-invite-to-channels) who can subscribe and
unsubscribe other users to channels.

## View channel subscribers

{start_tabs}

{tab|via-channel-settings}

{relative|channel|all}

1. Select a channel.

{!select-channel-view-subscribers.md!}

{!channel-menu-subscribers-tab-tip.md!}

{tab|via-right-sidebar}

1. Click on a channel in the left sidebar.

1. View subscribers in the **In this channel** section in the right sidebar. If
   the section is collapsed, click **In this channel** to reveal it.

!!! tip ""

    To see the full list of subscribers for a channel that has more than 600
    people subscribed, scroll to the bottom of the **In this channel** section,
    and click **View all subscribers**.

{end_tabs}

## Related articles

* [Introduction to channels](/help/introduction-to-channels)
* [Unsubscribe from a channel](/help/unsubscribe-from-a-channel)
* [Manage a user's channel subscriptions](/help/manage-user-channel-subscriptions)
* [Add or remove users from a channel](/help/add-or-remove-users-from-a-channel)
* [Set default channels for new users](/help/set-default-channels-for-new-users)

'''

def run():
    lines = test_markdown.split("\n")
    md_engine = markdown.Markdown
    t = TabbedSectionsPreprocessor(md_engine, {})
    lines = TabbedSectionsPreprocessor.run(t, lines)
    relativeLinks = RelativeLinks(md_engine)
    lines = relativeLinks.run(lines)
    # md_macro_extension = zerver.lib.markdown.include.makeExtension(base_path="help/include/")
    print('YOOOOOOOOOOOOOOOOOOO')
    print("\n".join(lines))
    print('ENDDDDDDDDDDDDdDDDDDDDDD')

run()
