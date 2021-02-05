from django import template

register = template.Library()


@register.filter(name='multiselect_summary')
def multiselect_summary(selections, default_text):
    if not selections:
        return default_text

    if (count := len(selections)) > 2:
        return f'Multi ({count})'

    return ', '.join(selections)
