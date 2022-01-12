from django.apps import AppConfig
from actstream.apps import ActstreamConfig


class CtsFormsConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'cts_forms'

    def ready(self):
        import cts_forms.signals  # noqa

        from actstream import registry
        registry.register(self.get_model('Report'))


class CtsActstreamConfig(ActstreamConfig):
    # Override default Actstream configuration to remove warning about AutoField
    default_auto_field = 'django.db.models.AutoField'
