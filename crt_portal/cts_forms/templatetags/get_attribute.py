from django import template


register = template.Library()


@register.filter(name='get_attribute')
def get_attribute(obj, attribute_name):
    return getattr(obj, attribute_name, None)
