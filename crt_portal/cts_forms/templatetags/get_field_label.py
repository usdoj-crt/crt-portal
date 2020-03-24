from django import template
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
register = template.Library()


@register.filter(name='get_field_label')
def get_field_label(value, arg):
    """
    Return label for given model/field from cts_forms app
    If no field exists, we expect it's a filter field like
    `create_date_end',  strip underscores for display
    """
    try:
        model = apps.get_model('cts_forms', value)
        field = model._meta.get_field(arg)
    except FieldDoesNotExist:
        return arg.replace('_', ' ')
    return field.verbose_name
