from django.core.validators import RegexValidator
from django.db import models


NewsWidgetNameValidator = RegexValidator(
    r'^[a-z0-9\-]+$',
    'Name may only contain lowercase letters a-z, digits 0-9, and the dash (-) character.',
)


class NewsWidgetColumnData(models.Model):

    class Meta:
        app_label = 'news_widget'
        verbose_name = 'News widget column'
        verbose_name_plural = 'News widget columns'

    name = models.CharField(
        max_length=256,
        unique=True,
        blank=False,
        null=False,
        validators=[NewsWidgetNameValidator],
        help_text="A unique name used to identify this news column's data. Data is fetched by this name.",
    )
    data = models.JSONField(
        default=list,
        blank=True,
        help_text='The list of news articles formatted as JSON for a news widget column',
    )

    def __str__(self):
        return self.name
