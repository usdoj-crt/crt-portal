import uuid

from django import template

register = template.Library()


@register.simple_tag
def random_id():
    """Returns a UUID for use as a random ID"""
    return str(uuid.uuid4())
