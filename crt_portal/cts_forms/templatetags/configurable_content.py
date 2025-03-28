from django import template
from django.utils.safestring import mark_safe

from ..models import ConfigurableContent

register = template.Library()


@register.simple_tag()
def configurable_content(machine_name):

    content = ConfigurableContent.objects.filter(machine_name=machine_name).first()
    if not content:
        return mark_safe('Missing content for {}'.format(machine_name))  # nosec
    return mark_safe(content.render())  # nosec
