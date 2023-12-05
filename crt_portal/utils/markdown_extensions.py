from markdown import Extension
from markdown.inlinepatterns import LinkInlineProcessor
from markdown.inlinepatterns import LINK_RE
from urllib.parse import urlparse, urljoin

from .site_prefix import get_site_prefix


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
