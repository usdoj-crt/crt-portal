from django import template


register = template.Library()


@register.filter(name='get_dict_item')
def get_dict_item(value, arg):
    # Use try over .get() to support defaultdict
    try:
        return value[arg]
    except KeyError:
        return None
