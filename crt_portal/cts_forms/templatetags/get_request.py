from django import template
from utils import request_utils

register = template.Library()


@register.simple_tag
def get_request_user():
    return request_utils.get_user()
