from django import template
from django.utils.translation import gettext_lazy as _

from ..model_variables import PRIMARY_COMPLAINT_DICT

register = template.Library()


@register.inclusion_tag('forms/snippets/primary_complaint_view.html')
def render_primary_complaint_view(primary_complaint):

    primary_complaint = PRIMARY_COMPLAINT_DICT.get(primary_complaint)

    return {
        'primary_complaint': primary_complaint,
    }