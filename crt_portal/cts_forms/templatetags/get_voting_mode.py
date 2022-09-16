
from django.conf import settings

from django import template

register = template.Library()


@register.simple_tag
def voting_mode():
    return settings.VOTING_MODE
