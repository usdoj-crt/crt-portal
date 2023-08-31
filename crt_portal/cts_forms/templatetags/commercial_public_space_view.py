from django import template
from django.utils.translation import gettext_lazy as _

from ..model_variables import COMMERCIAL_PUBLIC_FRIENDLY_TEXT

register = template.Library()


@register.inclusion_tag('forms/snippets/commercial_public_space_view.html')
def render_commercial_public_space_view(location, type, is_referral_view=False):
    other_text = None

    if location != 'other':
        location_type = COMMERCIAL_PUBLIC_FRIENDLY_TEXT.get(location, '—')
    else:
        location_type = type
        other_text = _('Other')

    return {
        'location_type': location_type,
        'other_text': other_text,
        'is_referral_view': is_referral_view
    }
