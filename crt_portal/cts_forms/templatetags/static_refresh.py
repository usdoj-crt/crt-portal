import base64
import os

import urllib.parse as urlparse
from urllib.parse import urlencode

from django import template
from django.conf import settings
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


@register.simple_tag
def static_embed(path):
    """Returns an html tag with the image data embedded."""
    if not path.startswith('img/'):
        raise ValueError('static_embed only supports images')
    filetype = path.split('.')[-1]

    source = os.path.join(settings.BASE_DIR, 'static', path)
    with open(source, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    return f'data:image/{filetype};base64,{content}'


def _add_params_to_url(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)
