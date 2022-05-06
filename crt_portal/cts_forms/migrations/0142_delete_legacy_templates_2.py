# Generated by Django 3.2.12 on 2022-02-11 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0141_delete_legacy_templates'),
    ]

    def remove_legacy_templates_2(apps, schema_editor):
        templates_to_remove = [
            'HCE - Referral for Housing/Lending/Public Accommodation',
            'HCE - Referral for Housing/Lending/Public Accommodation (Korean)',
            'HCE - Referral for Housing/Lending/Public Accommodation (Tagalog)',
            'HCE - Referral for Housing/Lending/Public Accommodation (Vietnamese)',
            'HCE - Referral for Housing/Lending/Public Accommodation (Chinese Simplified)',
            'HCE - Referral for Housing/Lending/Public Accommodation (Chinese Traditional)',
            'HCE - Referral for Housing/Lending/Public Accommodation (Spanish)',
        ]
        ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
        for title_to_remove in templates_to_remove:
            try:
                ResponseTemplate.objects.get(title=title_to_remove).delete()
            except ResponseTemplate.DoesNotExist:
                print(f'{title_to_remove} does not exist')

    operations = [
        migrations.RunPython(remove_legacy_templates_2)
    ]