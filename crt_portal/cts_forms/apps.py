from django.apps import AppConfig


class CtsFormsConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'cts_forms'

    def ready(self):
        import cts_forms.signals  # noqa

        from actstream import registry
        registry.register(self.get_model('Report'))
