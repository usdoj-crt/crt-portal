from django.db import migrations
from cts_forms.models import ProtectedClass

PROTECTED_CLASS_CHOICES = (
    _('Race/color'),
    _('National origin (including ancestry and ethnicity)'),
    _('Immigration/citizenship status (choosing this will not share your status)'),
    _('Religion'),
    _('Sex or gender identity (including gender stereotypes) or pregnancy'),
    _('Sexual orientation'),
    _('Disability (including temporary or recovery)'),
    _('Language'),
    _('Family, marriage, or parental status'),
    _('Military status'),
    _('Age'),
    _('Genetic information'),
    _('None of these apply to me'),
    _('Other reason'),
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
