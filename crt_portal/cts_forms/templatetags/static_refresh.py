import os

from django import template
from django.templatetags.static import StaticNode

register = template.Library()


class TimestampedStaticNode(StaticNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = str(int(os.path.getmtime('/code/package.json')))

    def url(self, *args, **kwargs):
        url = super().url(*args, **kwargs)
        return f'{url}?v={self.timestamp}'


@register.tag('static')
def do_static(parser, token):
    return TimestampedStaticNode.handle_token(parser, token)
