from cts_forms.models import ShutdownMode


def is_shutdown_mode():
    try:
        return ShutdownMode.objects.first().toggle
    except AttributeError:
        ShutdownMode.objects.create(toggle=False)
        return False
