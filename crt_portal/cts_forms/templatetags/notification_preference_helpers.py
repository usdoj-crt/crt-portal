from django import template


register = template.Library()


@register.filter(name='get_preference_value')
def get_preference_value(preferences, key):
    if not preferences:
        return 'none'
    return getattr(preferences, key)

@register.filter(name='get_threshold_preference_value')
def get_threshold_preference_value(preferences, id):
    if not preferences:
        return 'none'
    return preferences.get(str(id), None)
