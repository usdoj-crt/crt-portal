from django.db import migrations


def add_drs_eeoc_referral_letter(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Response: Your Civil Rights Division Report - {{ record_locator }} from {{ section_name }} Section'
    ResponseTemplate.objects.create(
        title='DRS - EEOC Referral Form Letter',
        subject=subject,
        body="""
{{ addressee }},

Thank you for contacting the Department of Justice on {{ date_of_intake }}.  We have reviewed the information you provided and have determined that the complaint raises issues that are more appropriately addressed by another federal agency.  We are, therefore, referring this complaint to the following agency for further action:

U.S. Equal Employment Opportunity Commission 
202-921-3210 (voice); 202-663-7063 (TTY)

What you can do:

The above agency will review your complaint.  While we will take no further action on this matter, you can contact the agency above to check the status of your complaint.

How you have helped:

Although we are unable to act on your complaint, your report can help us find issues affecting multiple people or communities. It also helps us understand emerging trends and topics.

Thank you for taking the time to contact the Department of Justice about your concerns.  

Sincerely,


U.S. Department of Justice
Civil Rights Division
""")


def remove_drs_eeoc_referral_letter(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    templates = ResponseTemplate.objects.filter(title__icontains='DRS - EEOC Referral Form Letter')
    templates.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0124_update_auto-reply-form-letter'),
    ]

    operations = [
        migrations.RunPython(add_drs_eeoc_referral_letter, remove_drs_eeoc_referral_letter)
    ]
