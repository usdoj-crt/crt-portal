from django import template


register = template.Library()


@register.filter(name='get_dict_item')
def get_dict_item(value, arg):
    return value.get(arg, None)
