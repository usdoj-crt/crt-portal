# This didn't work as expected adding the next migration to fix it.
from django.db import migrations, models
from cts_forms.models import HateCrimesandTrafficking
from cts_forms.model_variables import HATE_CRIMES_TRAFFICKING_MODEL_CHOICES

import logging

logger = logging.getLogger(__name__)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0041_update_trafficking_text'),
    ]

    def load_new_text(*args, **defaults):
        pass  # noqa

    operations = [
        migrations.RunPython(load_new_text),
    ]
