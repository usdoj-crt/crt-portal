from django import template
from ..model_variables import CORRECTIONAL_FACILITY_FRIENDLY_TEXT


register = template.Library()


@register.inclusion_tag('forms/snippets/correctional_facility_view.html')
def render_correctional_facility_view(facility, facility_type, is_referral_view=False):
    if facility == 'outside':
        location_type = CORRECTIONAL_FACILITY_FRIENDLY_TEXT.get(facility, '—')
    else:
        location_type = CORRECTIONAL_FACILITY_FRIENDLY_TEXT.get(facility_type, '—')

    return {
        'location_type': location_type,
        'is_referral_view': is_referral_view
    }
