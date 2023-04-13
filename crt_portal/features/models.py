from django.db import models
from django.core.validators import RegexValidator


FeatureNameValidator = RegexValidator(r'^[a-z\-]*$', 'Feature may only contain the letters a-z and the dash (-) character')


class Feature(models.Model):
    name = models.CharField(max_length=256, unique=True, blank=False, null=False, validators=[FeatureNameValidator], help_text="A unique name for the feature, using only lowercase letters and dashes (-)")
    description = models.TextField(blank=True, null=True, help_text="A description of the feature, if the name isn't sufficient to explain what it is.")
    enabled = models.BooleanField(default=False, help_text="Whether to show this feature in the application.")

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

    @classmethod
    def is_feature_enabled(cls, name):
        """Gets whether a feature is enabled.

        If the feature does not exist, returns None.

        This means that `if is_feature_enabled(feature)` will return "False" if the
        feature doesn't exist.
        """
        try:
            return cls.objects.get(name=name).enabled
        except cls.DoesNotExist:
            return None
