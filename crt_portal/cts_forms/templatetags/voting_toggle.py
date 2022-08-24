from django import template
from django.utils.safestring import mark_safe

from ..models import VotingMode
import json

register = template.Library()

voting_toggle_info = VotingMode.objects.first().toggle
print("voting_toggle_info: ", voting_toggle_info)

@register.simple_tag
def voting_toggle_mode():
    return mark_safe(json.dumps(voting_toggle_info))
