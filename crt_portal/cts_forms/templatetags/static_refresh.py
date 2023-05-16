import os

import urllib.parse as urlparse
from urllib.parse import urlencode

from django import template
from django.templatetags.static import StaticNode

register = template.Library()


class TimestampedStaticNode(StaticNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = str(int(os.path.getmtime('.')))

    def url(self, *args, **kwargs):
        url = super().url(*args, **kwargs)
        return _add_params_to_url(url, {'v': self.timestamp})


@register.tag('static')
def do_static(parser, token):
    return TimestampedStaticNode.handle_token(parser, token)


def _add_params_to_url(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)
