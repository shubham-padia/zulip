import os
import re
from typing import List, Match
from xml.etree.ElementTree import Element

from markdown import Extension, Markdown
from markdown.preprocessors import Preprocessor
from typing_extensions import override

from zerver.lib.exceptions import InvalidMarkdownIncludeStatementError
from zerver.lib.markdown.priorities import BLOCK_PROCESSOR_PRIORITIES


class IncludeExtension(Extension):
    def __init__(self, base_path: str) -> None:
        super().__init__()
        self.base_path = base_path

    @override
    def extendMarkdown(self, md: Markdown) -> None:
        md.preprocessors.register(
            IncludePreProcessor(md, self.base_path),
            "include",
            1000
        )


class IncludePreProcessor(Preprocessor):
    RE = re.compile(r"^ {,3}\{!([^!]+)!\} *$", re.M)

    def __init__(self, md: Markdown, base_path: str) -> None:
        super().__init__(md)
        self.base_path = base_path

    def handleMatch(self, m: Match[str]) -> str:
        try:
            with open(os.path.normpath(os.path.join(self.base_path, m[1]))) as f:
                lines = f.read().splitlines()
        except OSError as e:
            raise InvalidMarkdownIncludeStatementError(m[0].strip()) from e

        for prep in self.md.preprocessors:
            lines = prep.run(lines)

        return "\n".join(lines)

    @override
    def run(self, lines: List[str]) -> List[str]:
        done = False
        while not done:
            for line in lines:
                loc = lines.index(line)
                match = self.RE.search(line)

                if match:
                    text = [self.handleMatch(match)]
                    # The line that contains the directive to include the macro
                    # may be preceded or followed by text or tags, in that case
                    # we need to make sure that any preceding or following text
                    # stays the same.
                    line_split = self.RE.split(line, maxsplit=0)
                    preceding = line_split[0]
                    following = line_split[-1]
                    text = [preceding, *text, following]
                    lines = lines[:loc] + text + lines[loc + 1 :]
                    break
            else:
                done = True
        return lines


def makeExtension(base_path: str) -> IncludeExtension:
    return IncludeExtension(base_path=base_path)
