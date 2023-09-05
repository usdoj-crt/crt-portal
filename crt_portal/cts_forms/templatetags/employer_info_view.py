from django import template
from ..model_variables import EMPLOYER_FRIENDLY_TEXT


register = template.Library()


@register.inclusion_tag('forms/snippets/employer_info_view.html')
def render_employer_info_view(employer_type, employee_size, is_referral_view=False):
    return {
        'employer_type': EMPLOYER_FRIENDLY_TEXT.get(employer_type, '-'),
        'employee_size': EMPLOYER_FRIENDLY_TEXT.get(employee_size, '-'),
        'is_referral_view': is_referral_view
    }
