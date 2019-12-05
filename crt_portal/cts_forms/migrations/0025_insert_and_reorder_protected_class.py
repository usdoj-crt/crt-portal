from django.db import migrations
from cts_forms.models import ProtectedClass
from cts_forms.model_variables import PROTECTED_CLASS_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0021_remove_location_fields_defaults'),
    ]

    def retrieve_or_create_choices(*args, **defaults):
        try:
            c = ProtectedClass.objects.filter(protected_class='National origin (including ancestry, and ethnicity)')

            c.update(protected_class='National origin (including ancestry, and ethnicity)')
        except DoesNotExist:
            pass

        order = 0
        for choice in PROTECTED_CLASS_CHOICES:
            c = ProtectedClass.objects.get_or_create(protected_class=choice)
            c[0].form_order = order
            order += 1

    operations = [
        migrations.RunPython(retrieve_or_create_choices),
    ]
