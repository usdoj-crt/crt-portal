from django.db import migrations


# This must match PROTECTED_CLASS_FIELDS in model_variables.py
PROTECTED_CLASS_FIELDS = [
    # (form order, code, display name)
    (0, 'Age', 'Age'),
    (1, 'Disability', 'Disability (including temporary or recovered and including HIV and drug addiction)'),
    (2, 'Family status', 'Family, marital, or parental status'),
    (3, 'Gender', 'Gender identity (including gender stereotypes)'),
    (4, 'Genetic', 'Genetic information (including family medical history)'),
    (5, 'Gun ownership', 'Gun Ownership'),
    (6, 'Immigration', 'Immigration/citizenship status (choosing this will not share your status)'),
    (7, 'Language', 'Language'),
    (8, 'National origin', 'National origin (including ancestry and ethnicity)'),
    (9, 'Pregnancy', 'Pregnancy'),
    (10, 'Race/color', 'Race/color'),
    (11, 'Religion', 'Religion'),
    (12, 'Sex', 'Sex'),
    (13, 'Orientation', 'Sexual orientation'),
    (14, 'None', 'None of these apply to me'),
    (15, 'Other', 'Other reason'),
]


def add_gun_ownership_and_reorder(apps, schema_editor):
    ProtectedClass = apps.get_model('cts_forms', 'ProtectedClass')

    for field in PROTECTED_CLASS_FIELDS:
        form_order, code, display_name = field
        try:
            # DO NOT look up by display_name as this has changed over time
            # And will cause lookups to fail, causing django to try
            # inserting duplicate records, thus the migration will fail
            #
            # Instead, Look up by code, which has been stable
            # across past migrations so we can ensure uniqueness
            obj = ProtectedClass.objects.get(code=code)
            obj.form_order = form_order
            obj.protected_class = display_name
            obj.save()
        except ProtectedClass.DoesNotExist:
            # New entry — create it
            ProtectedClass.objects.create(
                protected_class=display_name,
                value=code.lower().replace(' ', '_'),
                code=code,
                form_order=form_order,
            )


def reverse_migration(apps, schema_editor):
    """Remove the Gun Ownership row and restore original form_order values."""
    ProtectedClass = apps.get_model('cts_forms', 'ProtectedClass')

    # Delete the new row
    ProtectedClass.objects.filter(protected_class='Gun Ownership').delete()

    # Restore original ordering (before Gun was inserted at position 5)
    ORIGINAL_FIELDS = [
        (5, 'Immigration', 'Immigration/citizenship status (choosing this will not share your status)'),
        (6, 'Language', 'Language'),
        (7, 'National origin', 'National origin (including ancestry and ethnicity)'),
        (8, 'Pregnancy', 'Pregnancy'),
        (9, 'Race/color', 'Race/color'),
        (10, 'Religion', 'Religion'),
        (11, 'Sex', 'Sex'),
        (12, 'Orientation', 'Sexual orientation'),
        (13, 'None', 'None of these apply to me'),
        (14, 'Other', 'Other reason'),
    ]
    for form_order, code, display_name in ORIGINAL_FIELDS:
        try:
            obj = ProtectedClass.objects.get(protected_class=display_name)
            obj.form_order = form_order
            obj.save()
        except ProtectedClass.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0236_mediationnumbertracker_report_mediation_and_more'),
    ]

    operations = [
        migrations.RunPython(add_gun_ownership_and_reorder, reverse_migration),
    ]
