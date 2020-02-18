from django import template

register = template.Library()


@register.filter(name='withInputError')
def with_input_error(field, arg='usa-input--error'):
    if bool(field.errors):
        css_classes = field.field.widget.attrs.get('class', None)
        return field.as_widget(attrs={'class': f"{arg} {css_classes}"})

    return field
