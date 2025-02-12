from django import template
from utils.shutdown_mode import is_shutdown_mode

register = template.Library()


@register.simple_tag
def get_shutdown_mode():
    mode = is_shutdown_mode()
    print("ShutdownMode = ", mode)
    return mode
