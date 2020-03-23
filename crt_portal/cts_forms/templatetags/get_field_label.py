from django import template
from django.apps import apps

register = template.Library()


@register.filter(name='get_field_label')
def get_field_label(value, arg):
    """Return label for given model/field from cts_forms app"""
    model = apps.get_model('cts_forms', value)
    field = model._meta.get_field(arg)
    return field.verbose_name
