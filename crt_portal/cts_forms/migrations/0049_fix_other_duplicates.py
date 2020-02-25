from django.db import migrations, models

from cts_forms.models import Report, ProtectedClass


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0046_update_primary_complaint'),
    ]

    def retrieve_or_create_choices(*args, **defaults):
        # remove other codes from "other" code from "Other", since codes are unique
        old_other = ProtectedClass.objects.get(code='Other')
        old_other.code = 'old'
        old_other.save()

        # label data should be attributed to
        real_other = ProtectedClass.get_or_create(protected_class='Other reason')
        real_other.form_order = 14
        real_other.code = 'Other'
        real_other.save()
        # pull records that need to be updated
        update_records = Report.objects.filter(protected_class__protected_class__in=['other', 'Other'])
        # loop through the records to add the correct relationship
        for record in update_records:
            record.protected_class.add(real_other)

        # remove the incorrect "other" variants
        ProtectedClass.objects.get(protected_class='Other').delete()
        try:
            ProtectedClass.objects.get(protected_class='other').delete()
        except ProtectedClass.DoesNotExist:
            pass

    operations = [
        migrations.RunPython(retrieve_or_create_choices),
    ]
