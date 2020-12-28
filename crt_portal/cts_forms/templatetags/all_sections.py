from django import template

from ..model_variables import SECTION_CHOICES

register = template.Library()


@register.simple_tag
def filter_for_all_sections():
    """Return string of query parameters specifying a filter to include all sections"""
    sections = ''.join([f'&assigned_section={section}' for section, _ in SECTION_CHOICES])
    return sections
