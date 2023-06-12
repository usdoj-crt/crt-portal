from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..models import BannerMessage

register = template.Library()


@register.simple_tag
def banner_message():
    banners = [
        render_to_string('partials/banner_message.html', {'message': message})
        for message in
        BannerMessage.objects.filter(show=True).order_by('order')
    ]

    return mark_safe('\n'.join(banners))  # nosec
