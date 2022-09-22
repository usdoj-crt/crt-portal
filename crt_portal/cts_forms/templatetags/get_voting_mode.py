import os
# from django.conf import settings

from django import template

register = template.Library()


@register.simple_tag
def voting_banner():
    return os.environ.get('VOTING_MODE', False)
