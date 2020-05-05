from django.db import migrations, models

# original list
PROTECTED_CLASS_FIELDS = [
    # (form order, code, display name)
    (0, 'Age', 'Age'),
    (1, 'Disability', 'Disability (including temporary or recovery)'),
    (2, 'Family status', 'Family, marital, or parental status'),
    (3, 'Gender', 'Gender identity (including gender stereotypes)'),
    (4, 'Genetic', 'Genetic information (including family medical history)'),
    (5, 'Immigration', 'Immigration/citizenship status (choosing this will not share your status)'),
    (6, 'Language', 'Language'),
    (7, 'National origin', 'National origin (including ancestry and ethnicity)'),
    (8, 'Pregnancy', 'Pregnancy'),
    (9, 'Race/color', 'Race/color'),
    (10, 'Religion', 'Religion'),
    (11, 'Sex', 'Sex'),
    (12, 'Orientation', 'Sexual orientation'),
    (13, 'None', 'None of these apply to me'),
    (14, 'Other', 'Other'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0044_update_protected_class'),
    ]

    def retrieve_or_create_choices(apps, schema_editor):
        ProtectedClass = apps.get_model('cts_forms', 'ProtectedClass')
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
