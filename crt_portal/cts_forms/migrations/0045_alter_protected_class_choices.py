from django.db import migrations, models

from cts_forms.models import ProtectedClass
from cts_forms.model_variables import PROTECTED_CLASS_FIELDS


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0044_update_protected_class'),
    ]

    def retrieve_or_create_choices(*args, **defaults):
        try:
            # rename an existing objects
            g = ProtectedClass.objects.get(protected_class='Sex or gender identity (including gender stereotypes) or pregnancy')
            g.protected_class = 'Gender identity (including gender stereotypes)'
            g.save()
            f = ProtectedClass.objects.get(protected_class='Family, marriage, or parental status')
            f.protected_class = 'Family, marital, or parental status'
            f.save()
            g = ProtectedClass.objects.get(protected_class='Genetic information')
            g.protected_class = 'Genetic information (including family medical history)'
            g.save()
            # remove form order from old object
            m = ProtectedClass.objects.get(protected_class='Military status')
            m.form_order = None
            m.code = 'military'
            m.save()
        except ProtectedClass.DoesNotExist:
            pass

        # Add code and new form order to all objects
        for field in PROTECTED_CLASS_FIELDS:
            c = ProtectedClass.objects.get_or_create(protected_class=field[2])[0]
            c.form_order = field[0]
            c.code = field[1]
            c.protected_class = field[2]
            c.save()

    operations = [
        migrations.RunPython(retrieve_or_create_choices),
    ]
