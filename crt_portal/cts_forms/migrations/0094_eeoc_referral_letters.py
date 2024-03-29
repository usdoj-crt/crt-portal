# Generated by Django 2.2.17 on 2020-12-28 23:14

from django.db import migrations


def add_eeoc_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Response: Your Civil Rights Division Report - {{ record_locator }} from {{ section_name }} Section'
    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter',
        subject=subject,
        body="""
{{ addressee }},

You contacted the Department of Justice on {{ date_of_intake }}. After careful review of what you submitted, we have determined that your report would more appropriately be handled by another federal agency.

What we did:

Your record number is {{ record_locator }}.

Team members from the Civil Rights Division reviewed the information you submitted.  Based on your report, our team determined that you alleged employment discrimination or other employment-related issues.

Federal law limits the Department of Justice’s ability to take direct action under certain situations. Based on our team’s review of your report, this includes your matter.

What you can do:

We are not determining that your report lacks merit.  Rather, another federal agency may be able to help in your situation.

We have included a list of federal agencies that may be able to help. You should reach out to the appropriate agency if you want to pursue this further.

NOTE: There are strict time limits for filing complaints related to employment discrimination. If you feel you have been discriminated against in employment, you should contact the appropriate agency as soon as possible.

I EXPERIENCED...

Employment discrimination based on: race, color, national origin, religion, sex (including pregnancy, sexual orientation and gender identity), age, disability, or retaliation.

AGENCY THAT MAY BE ABLE TO HELP

Equal Employment Opportunity Commission (EEOC)

    File online: eeoc.gov/filing-charge-discrimination
    Contact by phone: 1-800-669-4000
    File in-person at your nearest EEOC Office: www.eeoc.gov/field-office

I EXPERIENCED...

Employment discrimination based on military service, including retaliation and failure to reemploy.

AGENCY THAT MAY BE ABLE TO HELP

U.S. Department of Labor
Veterans Employment Training Service (VETS)

    File online or contact VETS in-person: www.dol.gov/agencies/vets/
    Contact by phone: 1-866-487-2365

I EXPERIENCED...

Employment discrimination by the federal government

AGENCY THAT MAY BE ABLE TO HELP

The equal employment opportunity officer at your federal agency

    Find your federal EEO officer: www.eeoc.gov/federal-sector/federal-agency-eeo-directors

I EXPERIENCED...

A workers’ compensation issue

AGENCY THAT MAY BE ABLE TO HELP

U.S. Department of Labor
Office of Workers’ Compensation Programs (OWCP)

    Phone and in-person options:
    https://www.dol.gov/owcp/owcpkeyp.htm

I EXPERIENCED...

An issue with wages and/or work hours

AGENCY THAT MAY BE ABLE TO HELP

U.S. Department of Labor
Employment Standards Administration, Wage and Hour Division

    How to file a complaint: www.dol.gov/agencies/whd/contact/complaints
    Contact by phone: 1-866-487-2365

I EXPERIENCED...

An issue with worker safety

AGENCY THAT MAY BE ABLE TO HELP

U.S. Department of Labor
Occupational Health and Safety Administration (OSHA)

    File online: www.osha.gov/workers/
    Contact by phone: 1-800-321-6742

I EXPERIENCED...

A problem with the Equal Employment Opportunity Commission

AGENCY THAT MAY BE ABLE TO HELP

Equal Employment Opportunity Commission
Director, Office of Field Management Programs

    131 M Street, NE
    Washington, DC 20507

In addition, your state bar association or local legal aid office may be able to help with your issue even though the Department of Justice cannot.

TO FIND...

A personal attorney

ORGANIZATION THAT MAY BE ABLE TO HELP

American Bar Association

    www.findlegalhelp.org
    Contact by phone: 1-800-285-2221

TO FIND...

A personal attorney for low-income individuals

ORGANIZATION THAT MAY BE ABLE TO HELP

Legal Services Corporation (or Legal Aid Offices)

    www.lsc.gov/find-legal-aid

How you helped:

While we cannot act in this specific instance, your report will help us advance civil rights. Information from reports such as yours helps us understand emerging and urgent issues.  This helps inform how we protect the civil rights of all people in this country.

Thank you for taking the time to contact the Department of Justice about your concerns.

Sincerely,

U.S. Department of Justice
Civil Rights Division
        """)
    subject_es = 'Respuesta: Su informe de la División de Derechos Civiles - {{ record_locator }} de la Sección {{ es.section_name }}'
    ResponseTemplate.objects.create(
        title='CRT - EEOC Referral Letter (Spanish)',
        subject=subject_es,
        body="""
{{ es.addressee }},

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Tras revisar detenidamente el reporte que usted sometió, hemos determinado que sería más apropiado que otra agencia federal se encargara de su reporte.

Lo que nosotros hicimos:

Su número de registro es {{ record_locator }}.

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted sometió. Con base en su informe, nuestro equipo ha determinado que usted está alegando que hubo discriminación en el empleo o algún otro problema relacionado con el empleo.

Las leyes federales limitan la capacidad del Departamento de Justicia de tomar medidas directas en ciertas circunstancias. Con base en la revisión de su reporte por parte de nuestro equipo, esto se aplica al asunto que usted menciona.

Lo que usted puede hacer:

No hemos determinado que su reporte carece de mérito, sino que otra agencia tal vez pueda ayudarle con su problema.

Hemos incluido una lista de agencias federales que podrían ser de ayuda. Si desea continuar adelante con este asunto, debe comunicarse con la agencia apropiada.

N.B.: Existen plazos estrictos para la presentación de demandas relacionadas con discriminación en el empleo. Si usted cree haber sido víctima de discriminación en el empleo, debe comunicarse con la agencia apropiada cuanto antes.

EXPERIMENTÉ...

Discriminación en el empleo por motivos de: raza, color de piel, origen nacional, religión, género (incluyendo embarazo, orientación sexual e identidad de género), edad, discapacidad o represalias.

LA AGENCIA QUE PODRÍA AYUDAR

Comisión para la Igualdad de Oportunidades (EEOC, por sus siglas en inglés)

    Presente una demanda virtual: eeoc.gov/filing-charge-discrimination
    Comuníquese por teléfono: 1-800-669-4000
    Presente una demanda en persona en la Oficina más cercana de la EEOC: www.eeoc.gov/field-office

EXPERIMENTÉ...

Discriminación en el empleo por motivos de servicio militar, incluyendo represalias y negación al reempleo.

LA AGENCIA QUE PODRÍA AYUDAR

Departamento del Trabajo de los EE. UU.
Servicio para la Capacitación Laboral de Veteranos (VETS, por sus siglas en inglés)

    Presente una demanda virtual o comuníquese con VETS en persona: www.dol.gov/agencies/vets/
    Comuníquese por teléfono: 1-866-487-2365

EXPERIMENTÉ...

Discriminación en el empleo por motivos de por parte del gobierno federal

LA AGENCIA QUE PODRÍA AYUDAR

El agente para la igualdad de oportunidades en el empleo (EEO, por sus siglas en inglés) de su agencia federal

    Localice a su agente federal de EEO: www.eeoc.gov/federal-sector/federal-agency-eeo-directors

EXPERIMENTÉ...

Un problema relacionado con la compensación al trabajador

LA AGENCIA QUE PODRÍA AYUDAR

Departamento del Trabajo de los EE. UU.
Oficina de Programas de Compensación al Trabajador (OWCP, por sus siglas en inglés)

    Opciones por teléfono y en persona:
    https://www.dol.gov/owcp/owcpkeyp.htm

EXPERIMENTÉ...

Un problema relacionado con el sueldo u horas laborales

LA AGENCIA QUE PODRÍA AYUDAR

Departamento del Trabajo de los EE. UU.
Administración para las Normas Laborales, División de Horas y Sueldos

    Cómo presentar una demanda: www.dol.gov/agencies/whd/contact/complaints
    Comuníquese por teléfono: 1-866-487-2365

EXPERIMENTÉ...

Un problema relacionado con la seguridad de los trabajadores

LA AGENCIA QUE PODRÍA AYUDAR

Departamento del Trabajo de los EE. UU.
Administración de Seguridad y Salud Ocupacional (OSHA, por sus siglas en inglés)

    Presente una demanda virtual: www.osha.gov/workers/
    Comuníquese por teléfono: 1-800-321-6742

EXPERIMENTÉ...

Un problema relacionado con la Comisión para la Igualdad de Oportunidades en el Empleo

LA AGENCIA QUE PODRÍA AYUDAR

Comisión para la Igualdad de Oportunidades en el Empleo
Director, Oficina de Programas de Gerencia Regional

    131 M Street, NE
    Washington, DC 20507

Por otra parte, su colegio de abogados estatal u oficina local de asistencia legal podrían ayudarle con su problema, aunque el Departamento de Justicia no puede.

PARA LOCALIZAR A:

Un abogado particular

LA ORGANIZACIÓN QUE PODRÍA AYUDAR

Colegio de Abogados Estadounidense

    www.findlegalhelp.org
    Comuníquese por teléfono: 1-800-285-2221

PARA LOCALIZAR A:

Un abogado particular para personas de bajos ingresos

LA ORGANIZACIÓN QUE PODRÍA AYUDAR

Corporación de Servicios Legales (u Oficinas de Asistencia Legal)

    www.lsc.gov/find-legal-aid

Cómo nos ha ayudado:

Aunque no podremos tomar medidas en esta situación en concreto, su informe nos ayudará a promover los derechos civiles. Información de informes como el suyo nos ayuda a entender problemas urgentes y emergentes. Esto nos ayuda a orientar cómo protegemos los derechos civiles de todos en este país.

Gracias por tomarse el tiempo para comunicarse con el Departamento de Justicia acerca de sus preocupaciones.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)


def remove_eeoc_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    templates = ResponseTemplate.objects.filter(title__icontains='EEOC Referral Letter')
    templates.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0093_referral'),
    ]

    operations = [
        migrations.RunPython(add_eeoc_letters, remove_eeoc_letters)
    ]
