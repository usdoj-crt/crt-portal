from django.db import migrations, models
from cts_forms.models import ProtectedClass
from cts_forms.model_variables import PROTECTED_CLASS_CHOICES


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0012_insert_protected_class_order'),
    ]

    def retrieve_or_create_options(*args, **defaults):
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='Immigration/citizenship status (choosing this does not share your status)').update(protected_class='Immigration/citizenship status (choosing this will not share your status)')
        except:  # noqa
            # if "Other" doesn't exist we don't have to rename it
            pass  # noqa
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='National Origin (including ancestry, ethnicity, and language)').update(protected_class='National origin (including ancestry, ethnicity, and language)')
            c.update()
        except:  # noqa
            # if "Other" doesn't exist we don't have to rename it
            pass  # noqa
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='Disability (including temporary or in recovery)').update(protected_class='Disability (including temporary or recovery)')
        except:  # noqa
            # if "Other" doesn't exist we don't have to rename it
            pass  # noqa
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='Other').update(protected_class='Other reason')
        except:  # noqa
            # if "Other" doesn't exist we don't have to rename it
            pass  # noqa

    operations = [
        migrations.RunPython(retrieve_or_create_options),
    ]
