from django.db import migrations
from cts_forms.models import ProtectedClass

PROTECTED_CLASS_CHOICES = (
    'Race/color',
    'National origin (including ancestry and ethnicity)',
    'Immigration/citizenship status (choosing this will not share your status)',
    'Religion',
    'Sex or gender identity (including gender stereotypes) or pregnancy',
    'Sexual orientation',
    'Disability (including temporary or recovery)',
    'Language',
    'Family, marriage, or parental status',
    'Military status',
    'Age',
    'Genetic information',
    'None of these apply to me',
    'Other reason',
)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0021_remove_location_fields_defaults'),
    ]

    def retrieve_or_create_choices(*args, **defaults):
        # rename an existing object
        try:
            c = ProtectedClass.objects.filter(protected_class='National origin (including ancestry, and ethnicity)')
            c.update(protected_class='National origin (including ancestry, and ethnicity)')
        except ProtectedClass.DoesNotExist:
            pass
        order = 0
        # Add new objects and set the order according to PROTECTED_CLASS_CHOICES
        for choice in PROTECTED_CLASS_CHOICES:
            c = ProtectedClass.objects.get_or_create(protected_class=choice)
            c[0].form_order = order
            c[0].save()
            order += 1

    operations = [
        migrations.RunPython(retrieve_or_create_choices),
    ]
