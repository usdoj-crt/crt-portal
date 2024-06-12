from django import template


register = template.Library()


@register.filter(name='get_preference_value')
def get_preference_value(preferences, key):
    if not preferences:
        return 'none'
    return getattr(preferences, key)
