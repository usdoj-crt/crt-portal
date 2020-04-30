from django.db import migrations, models
from cts_forms.model_variables import HATE_CRIMES_TRAFFICKING_MODEL_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0042_update_trafficking_data'),
    ]

    def load_new_text(apps, schema_editor):
        HateCrimesandTrafficking = apps.get_model('cts_forms', 'HateCrimesandTrafficking')
        try:
            hc_object = HateCrimesandTrafficking.objects.get(hatecrimes_trafficking_option='Coerced or forced to do work or perform a commercial sex act')
            hc_object.hatecrimes_trafficking_option = 'Coerced or forced to do work or perform a sex act in exchange for something of value'
            hc_object.save()
        except HateCrimesandTrafficking.DoesNotExist:
            pass

    operations = [
        migrations.RunPython(load_new_text),
    ]
