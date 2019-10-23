from django.apps import AppConfig


class CtsFormsConfig(AppConfig):
    name = 'cts_forms'

    def ready(self):
        import cts_forms.signals  # noqa
