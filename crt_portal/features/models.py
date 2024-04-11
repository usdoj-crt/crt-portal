from crequest.middleware import CrequestMiddleware

from django.core.validators import RegexValidator
from django.db import migrations, models
from django.db.utils import ProgrammingError
from django.contrib.auth.models import User

FeatureNameValidator = RegexValidator(r'^[a-z\-]*$', 'Feature may only contain the letters a-z and the dash (-) character')


class AddFeatureMigration(migrations.RunPython):
    def __init__(self, feature_name, enabled, *, description='', **kwargs):
        if '_' in feature_name:
            raise ValueError('Underscores are not allowed in feature names. Use dashes instead.')

        def add_feature(apps, schema_editor):
            drop_feature(apps, schema_editor)
            Feature.objects.create(name=feature_name,
                                   enabled=enabled,
                                   description=description)

        def drop_feature(apps, schema_editor):
            del apps, schema_editor  # unused
            try:
                Feature.objects.get(name=feature_name).delete()
            except Feature.DoesNotExist:
                pass

        super().__init__(add_feature, drop_feature, **kwargs)


class Feature(models.Model):

    class Meta:
        app_label = 'features'

    name = models.CharField(max_length=256, unique=True, blank=False, null=False, validators=[FeatureNameValidator], help_text="A unique name for the feature, using only lowercase letters and dashes (-)")
    description = models.TextField(blank=True, null=True, help_text="A description of the feature, if the name isn't sufficient to explain what it is.")
    enabled = models.BooleanField(default=False, help_text="Whether to show this feature in the application.")
    users_when_disabled = models.ManyToManyField(User, blank=True, help_text="Users who are allowed to see this feature. Note that enabled features will be visible to everybody, always.")

    def __str__(self):
        return self.name

    def title_case(self):
        return self.name.replace('-', ' ').title()

    def camel_case(self):
        firstLetter = self.name[0].lower()
        titleCase = self.name.replace('-', ' ').title().replace(' ', '')
        return (firstLetter + titleCase[1:])

    def snake_case(self):
        return self.name.replace('-', '_')

    def is_enabled(self):
        if self.enabled:
            return True
        request = CrequestMiddleware.get_request()
        if not request or not request.user:
            return False
        # Only allow if the current user is in the allowed list:
        return self.users_when_disabled.filter(id=request.user.id).exists()

    @classmethod
    def is_feature_enabled(cls, name):
        """Gets whether a feature is enabled.

        If the feature does not exist, returns None.

        This means that `if is_feature_enabled(feature)` will return "False" if the
        feature doesn't exist.
        """
        try:
            return cls.objects.get(name=name).is_enabled()
        # During tests, this might be run prior to migrations,
        # hence ProgrammingError
        except (cls.DoesNotExist, ProgrammingError):
            return None
