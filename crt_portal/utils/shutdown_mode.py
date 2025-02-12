from cts_forms.models import ShutdownMode


def is_shutdown_mode():
    try:
        shutdown_mode = ShutdownMode.objects.first()
        return shutdown_mode.toggle
    except AttributeError:
        ShutdownMode.objects.create(toggle=False)
        return False
