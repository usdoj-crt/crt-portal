import collections
from typing import Dict, List, Optional
from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import LinkInlineProcessor
from markdown.inlinepatterns import LINK_RE
from markdown.treeprocessors import Treeprocessor
# bandit flags ANY import from ElementTree, not just parse-related ones.
# Element is not a parser and there is no alternative to importing from `xml`.
from xml.etree.ElementTree import Element  # nosec
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

        should_remove = sorted([
            (option['start_char'], option['end_char'])
            for group, options in optionals.items()
            for option in options
            if option['name'] not in self.include.get(group, [])
        ], key=lambda startend: -startend[0])

        for start, end in should_remove:
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


class CustomHTMLProcessor(Treeprocessor):
    # Alter the HTML output to provide inline styles and other custom markup.
    # For more, see here: https://github.com/Python-Markdown/markdown/wiki/Tutorial-2---Altering-Markdown-Rendering
    # Why do we use inline styles for HTML emails? Although it doesn't seem
    # necessary for most modern email clients, this is a backward-compatibility
    # strategy.
    # https://www.litmus.com/blog/do-email-marketers-and-designers-still-need-to-inline-css/
    def run(self, root):
        for element in root.iter('h1'):
            element.set('style', 'margin-top: 36px; margin-bottom: 16px; font-size: 22px;color: #162e51;font-family: Merriweather,Merriweather Web,Merriweather Web,Tinos,Georgia,Cambria,Times New Roman,Times,serif;line-height: 1.5;font-weight: 700;')
            div = Element('div')
            div.set('style', 'margin-top: 8px; border: 2px solid #162e51; border-radius: 2px; background: #162e51; width: 25px;')
            element.append(div)
        for element in root.iter('h2'):
            element.set('style', 'margin-top: 36px; margin-bottom: 16px; font-size: 20px;color: #162e51;font-family: Merriweather,Merriweather Web,Merriweather Web,Tinos,Georgia,Cambria,Times New Roman,Times,serif;line-height: 1.5;font-weight: 700;')


class CustomHTMLExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(CustomHTMLProcessor(md), 'custom_html_processor', 15)
