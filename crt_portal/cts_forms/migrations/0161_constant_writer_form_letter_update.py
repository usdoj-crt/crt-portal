from django.db import migrations


def modify_constant_writer_form_letter(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    constant_writer_form_letter = ResponseTemplate.objects.get(title='CRT - Constant Writer')
    constant_writer_form_letter.subject = 'Response: Your Civil Rights Division Report - {{ record_locator }} from the {{ section_name }} Section'
    constant_writer_form_letter.save()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0160_gh1439_campaign_link_tracking'),
    ]

    operations = [
        migrations.RunPython(modify_constant_writer_form_letter)
    ]