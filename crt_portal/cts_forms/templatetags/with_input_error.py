from django import template

register = template.Library()

text_input_types = ['text', 'number', 'select']


def is_textarea(widget):
    return widget.__class__.__name__ == 'Textarea'


@register.filter(name='withInputError')
def with_input_error(field):
    widget = field.field.widget

    if bool(field.errors) and (is_textarea(widget) or widget.input_type in text_input_types):
        css_classes = widget.attrs.get('class', None)
        return field.as_widget(attrs={'class': f"usa-input--error error-focus {css_classes}"})

    if bool(field.errors) and widget.input_type in ['radio', 'checkbox']:
        css_classes = widget.attrs.get('class', None)
        return field.as_widget(attrs={'class': f"error-focus {css_classes}"})

    return field
