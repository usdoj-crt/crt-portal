import os

from django import template
from utils.site_prefix import get_site_prefix

register = template.Library()


@register.simple_tag
def environment():
    return os.environ.get('ENV', 'UNDEFINED')


@register.simple_tag
def intake_site_prefix():
    return get_site_prefix(for_intake=True)
