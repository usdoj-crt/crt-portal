from django.db import migrations


def modify_drs_dept_of_ed_referral_letter(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    doe_form_letter = ResponseTemplate.objects.get(title='DRS - Dept of Ed Referral Form Letter')
    doe_form_letter.body="""
Re:		Civil Rights Division Complaint – {{ record_locator }} from the Disability Rights Section

Thank you for contacting the Department of Justice on {{ date_of_intake }}.  We have reviewed the information you provided and have determined that the complaint raises issues that are more appropriately addressed by another federal agency.  We are, therefore, referring this complaint to the following agency for further action:

U.S. Department of Education, Office for Civil Rights 
(800) 421-3481; (202) 453-6012 (fax); (800) 877-8339 (TDD)
OCR@ed.gov

What you can do:

The above agency will review your complaint.  While we will take no further action on this matter, you can contact the agency above to check the status of your complaint.

How you have helped:

Although we are unable to act on your complaint, your report can help us find issues affecting multiple people or communities. It also helps us understand emerging trends and topics.

Thank you for taking the time to contact the Department of Justice about your concerns.  

Sincerely,


U.S. Department of Justice
Civil Rights Division
"""

    doe_form_letter.save()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0130_drs_hhs_referral_letter_update'),
    ]

    operations = [
        migrations.RunPython(modify_drs_dept_of_ed_referral_letter)
    ]
