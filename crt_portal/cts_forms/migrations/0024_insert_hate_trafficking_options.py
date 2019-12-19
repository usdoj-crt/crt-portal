from django.db import migrations
from cts_forms.models import HateCrimesandTrafficking
from cts_forms.model_variables import HATE_CRIMES_TRAFFICKING_MODEL_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0023_make_fields_longer'),
    ]

    def retrieve_or_create_choices(*args, **defaults):
        for choice in HATE_CRIMES_TRAFFICKING_MODEL_CHOICES:
            HateCrimesandTrafficking.objects.get_or_create(hatecrimes_trafficking_option=choice[1])

    operations = [
        migrations.RunPython(retrieve_or_create_choices),
    ]
