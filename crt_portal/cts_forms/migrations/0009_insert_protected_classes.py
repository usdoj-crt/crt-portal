from django.db import migrations
from cts_forms.models import ProtectedClass
from cts_forms.model_variables import PROTECTED_CLASS_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0008_auto_20191011_2101'),
    ]

    def retrieve_or_create_choices(*args, **defaults):
        for choice in PROTECTED_CLASS_CHOICES:
            c = ProtectedClass.objects.get_or_create(protected_class=choice)
            c[0].save()

    operations = [
        migrations.RunPython(retrieve_or_create_choices),
    ]
