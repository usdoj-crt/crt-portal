from django.db import migrations


def modify_crm_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    crm_r1_form_letter = ResponseTemplate.objects.get(title='CRM - R1 Form Letter')
    crm_r2_form_letter = ResponseTemplate.objects.get(title='CRM - R2 Form Letter')
    subject = 'Response: Your Civil Rights Division Report - {{ record_locator }} from the {{ section_name }} Section'
    crm_r1_form_letter.subject = subject
    crm_r2_form_letter.subject = subject
    crm_r1_form_letter.save()
    crm_r2_form_letter.save()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0162_constant_writer_form_letter_update'),
    ]

    operations = [
        migrations.RunPython(modify_crm_form_letters)
    ]
    