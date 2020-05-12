import os

from django import template

register = template.Library()


@register.simple_tag
def environment():
    return os.environ.get('ENV', 'UNDEFINED')
