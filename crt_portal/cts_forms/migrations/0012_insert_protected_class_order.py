from django.db import migrations, models
from cts_forms.models import ProtectedClass
from cts_forms.model_variables import PROTECTED_CLASS_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0011_insert_protected_classes'),
    ]

    def load_class_order(*args, **defaults):
        n = 0
        for choice in PROTECTED_CLASS_CHOICES:
            c = ProtectedClass.objects.get(protected_class=choice)
            c.form_order = n
            c.save()
            n += 1

    operations = [
        migrations.RunPython(load_class_order),
    ]
