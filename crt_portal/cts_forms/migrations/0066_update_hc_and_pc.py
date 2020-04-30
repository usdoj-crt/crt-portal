from django.db import migrations

from cts_forms.model_variables import (HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
                                       PROTECTED_CLASS_FIELDS, PROTECTED_MODEL_CHOICES)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0065_report_assigned_to'),
    ]

    def forward(apps, schema_editor):
        """
        Replace existing HateCrimesandTrafficking and ProtectedClass instances
        with those that conform to their defined choices
        """
        HateCrimesandTrafficking = apps.get_model('cts_forms', 'HateCrimesandTrafficking')
        ProtectedClass = apps.get_model('cts_forms', 'ProtectedClass')

        HateCrimesandTrafficking.objects.all().delete()
        ProtectedClass.objects.all().delete()

        for choice, label in HATE_CRIMES_TRAFFICKING_MODEL_CHOICES:
            HateCrimesandTrafficking.objects.get_or_create(hatecrimes_trafficking_option=choice)
        for form_order, code, display_name in PROTECTED_CLASS_FIELDS:
            # Matching logic used to create `cts_forms.model_variables.PROTECTED_MODEL_CHOICES`
            value = code.lower().replace(' ', '_')
            ProtectedClass.objects.get_or_create(protected_class=value, form_order=form_order, code=code)

    operations = [
        migrations.RunPython(forward),
    ]
