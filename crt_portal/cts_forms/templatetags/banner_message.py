from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..models import BannerMessage

register = template.Library()

DONT_SHOW_ON_ROUTES = [
    '/form/',
    '/admin/',
    '/accounts/',
]


@register.simple_tag(takes_context=True)
def banner_message(context):
    request = context.get('request', None)
    for route in DONT_SHOW_ON_ROUTES:
        if request and request.path.startswith(route):
            return ''

    banners = [
        render_to_string('partials/banner_message.html', {'message': message})
        for message in
        BannerMessage.objects.filter(show=True).order_by('order')
    ]

    return mark_safe('\n'.join(banners))  # nosec
