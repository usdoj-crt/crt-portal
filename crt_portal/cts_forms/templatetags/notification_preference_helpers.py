from django import template


register = template.Library()


@register.filter(name='get_preference_value')
def get_preference_value(preferences, key):
    if not preferences:
        return 'none'
    if getattr(preferences, key, False):
        return 'individual'
    return 'none'
