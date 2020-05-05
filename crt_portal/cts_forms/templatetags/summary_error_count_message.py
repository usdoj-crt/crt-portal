from django import template
from django.utils.translation import ngettext

register = template.Library()


@register.filter(name='summary_error_count_message')
def summary_error_count_message(count):
    """
    Return string describing number of error messages
    present on page
    """
    message = ngettext(f'{count} error found', f'{count} errors found', count)
    return message
