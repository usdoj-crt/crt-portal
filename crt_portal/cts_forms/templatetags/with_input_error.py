from django import template

register = template.Library()


input_types = ['text', 'number', 'select']


def is_textarea(widget):
    return widget.__class__.__name__ == 'Textarea'


@register.filter(name='withInputError')
def with_input_error(field, arg='usa-input--error'):
    widget = field.field.widget

    if bool(field.errors) and (is_textarea(widget) or widget.input_type in input_types):
        css_classes = widget.attrs.get('class', None)
        return field.as_widget(attrs={'class': f"{arg} {css_classes}"})

    return field
