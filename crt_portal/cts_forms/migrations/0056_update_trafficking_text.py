from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0055_update_trafficking'),
    ]

    def rename(apps, schema_editor):
        HateCrimesandTrafficking = apps.get_model('cts_forms', 'HateCrimesandTrafficking')

        try:
            hc_object = HateCrimesandTrafficking.objects.get(hatecrimes_trafficking_option='Coerced or forced to do work or perform a sex act in exchange for something of value')
            hc_object.hatecrimes_trafficking_option = 'Threatened, forced, and held against your will for the purposes of performing work or commercial sex acts. This could include threats of physical harm, withholding promised wages, or being held under a false work contract.'
            hc_object.save()
        except HateCrimesandTrafficking.DoesNotExist:
            pass

    operations = [
        migrations.RunPython(rename),
    ]
