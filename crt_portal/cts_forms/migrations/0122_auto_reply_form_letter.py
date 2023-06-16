from django.db import migrations


def add_auto_reply_form_letter(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Thank you for submitting a report to the Civil Rights Division'
    ResponseTemplate.objects.create(
        title='CRT Auto response',
        subject=subject,
        body="""
==================================================
Please do not reply to this email. This is an unmonitored account.
==================================================


Thank you for submitting a report to the Civil Rights Division. Please save your record number for tracking. Your record number is: {{ record_locator }}.


If you reported an incident where you or someone else has experienced or is still experiencing physical harm or violence, or are in immediate danger, please call 911 and contact the police.


---------------------------------


WHAT TO EXPECT
1. We review your report
Our specialists in the Civil Rights Division carefully read every report to identify civil rights violations, spot trends, and determine if we have authority to help with your report.


2. Our specialists determine the next steps
We may decide to:
- Open an investigation or take some other action within the legal authority of the Justice Department.
- Collect more information before we can look into your report.
- Recommend another government agency that can properly look into your report. If so, we’ll let you know.
In some cases, we may determine that we don’t have legal authority to handle your report and will recommend that you seek help from a private lawyer or local legal aid organization.


3. When possible, we will follow up with you
We do our best to let you know about the outcome of our review. However, we may not always be able to provide you with updates because:
* We’re actively working on an investigation or case related to your report.
* We’re receiving and actively reviewing many requests at the same time.
If we are able to respond, we will contact you using the contact information you provided in this report. Depending on the type of report, response times can vary. If you need to reach us about your report, please refer to your report number when contacting us. This is how we keep track of your submission.


---------------------------------


WHAT YOU CAN DO NEXT
1. Contact local legal aid organizations or a lawyer if you haven’t already
Legal aid offices or members of lawyer associations in your state may be able to help you with your issue.
* American Bar Association, visit www.findlegalhelp.org or call (800) 285-2221
* Legal Service Corporation (or Legal Aid Offices), visit www.lsc.gov/find-legal-aid


2. LEARN MORE: Visit civilrights.justice.gov to learn more about your rights and see examples of violations we handle.


---------------------------------


PLEASE NOTE: Each week, we receive hundreds of reports of potential violations.  We collect and analyze this information to help us select cases, and we may use this information as evidence in an existing case.  We will review your letter to decide whether it is necessary to contact you for additional information.  We do not have the resources to follow-up on every letter.
""")


def remove_auto_reply_form_letter(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    templates = ResponseTemplate.objects.filter(title__icontains='SPL - Standard Form Letter')
    templates.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0121_create_spl_tagalog'),
    ]

    operations = [
        migrations.RunPython(add_auto_reply_form_letter, remove_auto_reply_form_letter)
    ]
