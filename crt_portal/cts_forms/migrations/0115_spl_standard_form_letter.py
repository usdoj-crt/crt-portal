from django.db import migrations


def add_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Response: Your Civil Rights Division Report - {{ record_locator }} from {{ section_name }} Section'
    ResponseTemplate.objects.create(
        title='SPL - Standard Form Letter',
        subject=subject,
        body="""
{{ addressee }},

Thank you for your letter on {{ date_of_intake }}.  Your report number is {{ record_locator }}.  The Special Litigation Section relies on information from community members to identify civil rights violations.  Each week, we receive hundreds of reports of potential violations.  We collect and analyze this information to help us select cases, and we may use this information as evidence in an existing case.  We will review your letter to decide whether it is necessary to contact you for additional information.  We do not have the resources to follow-up on every letter.

The Special Litigation Section is one of several Sections in the Civil Rights Division.  We work to protect civil rights in four areas:  1) the rights of people in state or local institutions, including:  jails, prisons, juvenile detention facilities, and health care facilities for persons with disabilities (including whether persons in health care facilities should be getting services in the community instead); 2) the rights of people who interact with state or local police or sheriffs’ departments; 3) the rights of people to have safe access to reproductive health care clinics or religious institutions; and 4) the rights of people to practice their religion in state and local institutions.  We are not authorized to address issues with federal facilities or federal officials.  

If your concern is not within this Section’s area of work, you may wish to consult the Civil Rights Division web page to find the correct section:  https://civilrights.justice.gov/.  
  
The Special Litigation Section only handles cases that arise from widespread problems that affect groups of people.  We do not assist with individual problems.  We cannot help you recover damages or any personal relief.  We cannot assist in criminal cases, including wrongful convictions, appeals or sentencing.  

If you have an individual problem or seek compensation or some other form of personal relief, you may wish to consult a private attorney or a non-profit or legal aid organization for assistance.  There are only two areas in which we can assist an individual or address a single incident:  1) we may be able to assist you if you are being prevented from practicing your religion in a prison, jail, mental hospital or other facility operated by or for a state or local government; 2) we may be able to assist you if you have experienced force or the threat of force when accessing a reproductive health care facility or religious institution.
 
For more information about the Special Litigation Section or the work we do, please visit our web page:  www.justice.gov/crt/about/spl/.

Sincerely,
U.S. Department of Justice
Civil Rights Division
""")


def remove_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    templates = ResponseTemplate.objects.filter(title__icontains='SPL - Standard Form Letter')
    templates.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0114_auto_20210824_1705'),
    ]

    operations = [
        migrations.RunPython(add_spl_standard_form_letters, remove_spl_standard_form_letters)
    ]
