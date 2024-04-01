import collections
from typing import Dict, List, Optional
from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import LinkInlineProcessor
from markdown.inlinepatterns import LINK_RE
from urllib.parse import urlparse, urljoin

from .site_prefix import get_site_prefix

import re


class RelativeToAbsoluteLinkProcessor(LinkInlineProcessor):

    def __init__(self, *args, for_intake=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._site_prefix = get_site_prefix(for_intake)

    def getLink(self, *args, **kwargs):
        (href, title, index, handled) = super().getLink(*args, **kwargs)

        parsed = urlparse(href)

        if parsed.netloc:
            return (href, title, index, handled)

        return urljoin(self._site_prefix, href), title, index, handled


class RelativeToAbsoluteLinkExtension(Extension):

    def __init__(self, *args, for_intake=False, **kwargs):
        self._for_intake = for_intake
        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        priority = next(
            p.priority
            for p in md.inlinePatterns._priority
            if p.name == 'link'
        )

        md.inlinePatterns.deregister('link')

        pattern = RelativeToAbsoluteLinkProcessor(LINK_RE, md, for_intake=self._for_intake)
        md.inlinePatterns.register(pattern, 'link', priority)


# For example: [%optional group="The group label" name="The option name"]
# Note that `group` and `name` will be shown to users.
_OPTIONAL_START = (
    r'\[%\s*\s*optional\s+(?P<kwargs>[^\]]*)\]'
)
_OPTIONAL_END = r'\[%\s*endoptional\s*\]'
_OPTIONAL = re.compile(
    rf'{_OPTIONAL_START}(?P<content>.*?){_OPTIONAL_END}',
    re.DOTALL
)


def _parse_kwargs(kwargs: str) -> Dict[str, str]:
    return {
        key: value
        for key, value in re.findall(r'(\w+)="([^"]+)"', kwargs)
    }


def get_optionals(raw_markdown: str) -> Dict[str, List[Dict[str, str]]]:
    matches = [
        {
            **_parse_kwargs(match.group('kwargs')),
            'content': match.group('content').strip(),
            'start_char': match.start(),
            'end_char': match.end(),
        }
        for match in _OPTIONAL.finditer(raw_markdown)
    ]

    groups = collections.defaultdict(list)
    for match in matches:
        groups[match['group']].append(match)

    return groups


class OptionalProcessor(Preprocessor):
    def __init__(self, *args, include: Optional[Dict[str, List[str]]] = None, **kwargs):
        self.include = include or {}
        super().__init__(*args, **kwargs)

    def run(self, lines: list[str]) -> list[str]:
        raw_markdown = '\n'.join(lines)
        optionals = get_optionals(raw_markdown)

        should_remove = [
            (option['start_char'], option['end_char'])
            for group, options in optionals.items()
            for option in options
            if option['name'] not in self.include.get(group, [])
        ]

        for start, end in reversed(should_remove):
            raw_markdown = raw_markdown[:start] + raw_markdown[end:]

        raw_markdown = re.sub(_OPTIONAL_START, '', raw_markdown)
        raw_markdown = re.sub(_OPTIONAL_END, '', raw_markdown)

        return raw_markdown.split('\n')


class OptionalExtension(Extension):
    """Markdown extension to allow for optional content blocks.

    To use:
    - First, get a list of all optional blocks in the markdown content using `get_optionals`.
    - Then, pass in the `include` argument to the `OptionalExtension` constructor to specify which optional blocks should be included in the final output.

    For example:

    ```
    optionals = get_optionals(raw_markdown)

    include = {
        optionals[0]: optionals[0][0]['name']
        # e.g., 'The group label': ['The option name']
    }
    optional_extension = OptionalExtension(include=include)
    markdown = markdown.Markdown(extensions=[optional_extension])
    ```
    """

    def __init__(self, *args, include: Optional[Dict[str, List[str]]] = None, **kwargs):
        self.include = include
        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(OptionalProcessor(md, include=self.include), 'optional_processor', 1)
