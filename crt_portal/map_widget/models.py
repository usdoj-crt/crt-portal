from django.core.validators import RegexValidator
from django.db import models


MapWidgetNameValidator = RegexValidator(
    r'^[a-z0-9\-]+$',
    'Name may only contain lowercase letters a-z, digits 0-9, and the dash (-) character.',
)


class MapWidgetData(models.Model):

    class Meta:
        app_label = 'map_widget'
        verbose_name = 'Map widget data'
        verbose_name_plural = 'Map widget data'

    name = models.CharField(
        max_length=256,
        unique=True,
        blank=False,
        null=False,
        validators=[MapWidgetNameValidator],
        help_text="A unique name used to identify this map's data. The map widget fetches its data by this name.",
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text='The JSON data for the map',
    )

    def __str__(self):
        return self.name
