# Generated by Django 2.2.13 on 2020-09-01 18:18

from django.db import migrations


def add_spanish_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Respuesta: Su informe de la División de Derechos Civiles - {{ record_locator }} de la Sección {{ es.section_name }}'
    ResponseTemplate.objects.create(
        title='CRT - Non-Actionable (Spanish)',
        subject=subject,
        body="""
{{ es.addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake}}. Tras revisar detenidamente su presentación, decidimos no tomar medidas adicionales en lo que se refiere a su querella.

Lo que hicimos:

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted entregó. Con base en esta información, nuestro equipo determinó que las leyes federales de derechos civiles que nosotros hacemos cumplir no se aplican a la situación que usted describió. Por lo tanto, no podremos tomar medidas adicionales.

Su número de registro es {{ record_locator }}.

Lo que usted puede hacer:

Es posible que el asunto que usted planteó sea amparado bajo otras leyes federales, estatales o locales que no tenemos la autoridad de hacer cumplir. No hemos determinado que su presentación carece de mérito.

El colegio de abogados de su estado o una oficina local de asistencia legal podría ayudarle con su asunto, aunque el Departamento de Justicia no puede.

    Para localizar a una oficina local:

    American Bar Association [Colegio de Abogados de los Estados Unidos]
    www.findlegalhelp.org (solo en inglés)
    (800) 285-2221

    Legal Services Corporation [Corporación de Servicios Legales] (o Legal Aid Offices [Oficinas de Asistencia Legal])
    www.lsc.gov/find-legal-aid (solo en inglés)

Gracias por comunicarse con el Departamento de Justicia acerca de sus preocupaciones. Sentimos no poder ayudarle más con este asunto.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)
    ResponseTemplate.objects.create(
        title='CRT - No Capacity (Spanish)',
        subject=subject,
        body="""
{{ es.addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Tras revisar detenidamente su presentación, decidimos no tomar medidas adicionales en lo que se refiere a su querella.

Lo que hicimos:

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted entregó. Con base en nuestro repaso, hemos decidido no tomar medidas adicionales en lo que se refiere a su querella. Cada año, recibimos varios miles de reportes de vulneraciones de derechos civiles. Por desgracia no tenemos los recursos para tomar una acción directa para cada reporte.

Su número de registro era {{ record_locator }}.

Lo que usted puede hacer:

No hemos determinado que su presentación carece de mérito. Es posible que otra entidad pueda tomar medidas. En concreto, el colegio de abogados de su estado o su oficina local de asistencia legal podrían ayudarle.

    Para localizar a una oficina local:
    American Bar Association [Colegio de Abogados de los Estados Unidos]
    www.findlegalhelp.org (solo en inglés)
    (800) 285-2221

    Legal Services Corporation [Corporación de Servicios Legales] (o Legal Aid Offices [Oficinas de Asistencia Legal])
    www.lsc.gov/find-legal-aid (solo en inglés)

Cómo usted nos ha ayudado:

Aunque no tenemos la capacidad de asumir cada reporte individual, su reporte podrá ayudarnos a identificar problemas que afectan a múltiples personas o comunidades. Por otra parte, nos ayuda a entender tendencias y asuntos emergentes.

Gracias por comunicarse con el Departamento de Justicia acerca de sus preocupaciones. Sentimos no poder ayudarle más con este asunto.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)
    ResponseTemplate.objects.create(
        title='CRT - Comments & Opinions (Spanish)',
        subject=subject,
        body="""
{{ es.addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Su número de registro es {{ record_locator }}.

Agradecemos su interés y el tiempo que ha dedicado a escribirnos para expresar su perspectiva. Queremos que sepa que la información que usted nos brindó recibirá la consideración apropiada.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)
    ResponseTemplate.objects.create(
        title='CRT - Request for Agency Review (Spanish)',
        subject=subject,
        body="""
{{ es.addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Esta carta se escribe en respuesta a su reporte.

Lo que hicimos:

Su número de registro es {{ record_locator }}.

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted entregó. Usted indicó que ha presentado una querella de discriminación ante o contra otra agencia federal.

El Departamento de Justicia no sirve como autoridad revisora de las decisiones de otras agencias federales tras sus investigaciones de querellas de discriminación.

Por lo tanto, no tomaremos medidas adicionales.

Lo que usted puede hacer:

Esta carta no es una determinación que su reporte carece de mérito. Es posible que el colegio de abogados de su estado o su oficina local de asistencia legal podrían ayudarle.

PARA LOCALIZAR A...

Un abogado particular

UNA ORGANIZACIÓN QUE PODRÍA AYUDARLE

American Bar Association [Colegio de Abogados de los Estados Unidos]

    En Internet:
    www.findlegalhelp.org (solo en inglés)

    Por teléfono: (800) 285-2221

PARA LOCALIZAR A...

Un abogado particular para personas de bajos ingresos

UNA ORGANIZACIÓN QUE PODRÍA AYUDARLE

Legal Services Corporation [Corporación de Servicios Legales] (o Legal Aid Offices [Oficinas de Asistencia Legal])

    En Internet:
    www.lsc.gov/find-legal-aid (solo en inglés)

Cómo nos ha ayudado:

Aunque no podemos tomar medidas en esta instancia en concreto, su reporte nos ayudará a fomentar los derechos civiles. La información contenida en reportes como el suyo nos ayuda a entender asuntos emergentes y urgentes. Esto, a su vez, nos ayuda a informar cómo protegemos los derechos civiles de todas las personas en este país.

Gracias por comunicarse con el Departamento de Justicia acerca de sus preocupaciones.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)
    ResponseTemplate.objects.create(
        title='HCE - Referral for Housing/Lending/Public Accommodation (Spanish)',
        subject=subject,
        body="""
{{ es.addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}.

Lo que hicimos:

Su número de registro es {{ record_locator }}.

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted entregó. Con base en su reporte, nuestro equipo determinó que usted alegó que hubo discriminación en una o más de las siguientes áreas:

1) la vivienda
2) las instalaciones públicas, tales como hoteles y restaurantes; o
3) el ámbito crediticio.

Cabe destacar que en situaciones que implican estos tipos de discriminación, por lo general, la División de Derechos Civiles normalmente se involucra únicamente cuando grupos de personas sean afectados. Generalmente hablando, no iniciamos investigaciones con base en alegaciones individuales de discriminación.

Teniendo esto en cuenta, revisaremos su reporte detenidamente y nos comunicaremos con usted si necesitamos información adicional o si podemos iniciar una investigación.

Lo que usted puede hacer:

Si su reporte está relacionado con discriminación en la vivienda, el Departamento de Vivienda y Desarrollo Urbano («HUD», por sus siglas en inglés) podría ayudarle. HUD es la agencia responsable de revisar las querellas relacionadas con el ámbito de la vivienda que afecten a una sola persona.

N.B.: Existen plazos estrictos para la presentación de una querella de discriminación en la vivienda. Si usted cree haber sido víctima de discriminación en la vivienda, debe comunicarse cuanto antes con la agencia apropiada.

YO EXPERIMENTÉ...

Discriminación en la vivienda por motivos de:

- Raza o color de piel,
- Origen nacional,
- Religión,
- Género
- Estatus familiar,
- Discapacidad o
- Represalias

LA AGENCIA QUE PODRÍA AYUDAR:

Departamento de Vivienda y Desarrollo Urbano de los EE. UU.
Oficina de Vivienda Justa e Igualdad de Oportunidades

    Presentación virtual de querellas: https://portalapps.hud.gov/AdaptivePages/HUD_Spanish/Espanol/complaint/complaint-details.htm

    Por teléfono: (800) 669-9777

    Presentación en persona en su oficina local más cercana
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo (solo en inglés)

YO EXPERIMENTÉ...

Un problema con o una pregunta sobre:

- Subsidios o bonos de vivienda,
- Una autoridad de vivienda pública,
- Un empleado de una autoridad de vivienda pública o
- La recepción por parte de un propietario de un subsidio de vivienda

LA AGENCIA QUE PODRÍA AYUDAR:

Departamento de Vivienda y Desarrollo Urbano de los EE. UU.
Vivienda Pública e Indígena

    Centro de Atención al Cliente de PIH:
    www.hud.gov/program_offices/public_indian_housing (solo en inglés)

    Por teléfono: (800) 955-2232

YO EXPERIMENTÉ...

Un problema con o una pregunta sobre:

- El desamparo

LA AGENCIA QUE PODRÍA AYUDAR:

Departamento de la Vivienda y Desarrollo Urbano de los EE. UU.
Recursos sobre el desamparo

    En Internet:
    www.hudexchange.info/housing-and-homeless-assistance/ (solo en inglés)

YO EXPERIMENTÉ...

Fraude, desperdicio o abusos relacionados con:

- HUD o
- Un programa afiliado con HUD

LA AGENCIA QUE PODRÍA AYUDAR:

Departamento de Vivienda y Desarrollo Urbano de los EE. UU.
Oficina del Inspector General

    En Internet:
    www.hudoig.gov/hotline (solo en inglés)

    Por correo electrónico: hotline@hudoig.gov

Si su reporte está relacionado con discriminación en al ámbito crediticio, podrá presentar una querella ante HUD y la Oficina para la Protección Financiera del Consumidor (CFPB, por sus siglas en inglés). Estas agencias son responsables de revisar querellas que afecten a una sola persona.

N.B.: Existen plazos estrictos para la presentación de una querella de discriminación en el ámbito crediticio. Si usted cree haber sido víctima de discriminación en el ámbito crediticio, debe comunicarse cuanto antes con la agencia apropiada.

YO EXPERIMENTÉ...

Discriminación en la financiación de la adquisición de una vivienda (es decir, una hipoteca) por motivos de:

- Raza o color de piel,
- Origen nacional,
- Religión,
- Género
- Estatus familiar,
- Discapacidad o
- Represalias

LA AGENCIA QUE PODRÍA AYUDAR:

Departamento de Vivienda y Desarrollo Urbano de los EE. UU.
Oficina de Vivienda Justa e Igualdad de Oportunidades

    En Internet:
    https://portalapps.hud.gov/AdaptivePages/HUD_Spanish/Espanol/complaint/complaint-details.htm

    Por teléfono: (800) 669-9777

    Presentación en persona en su oficina local más cercana
    www.hud.gov/program_offices/fair_housing_equal_opp/contact_fheo (solo en inglés)

YO EXPERIMENTÉ...

Discriminación en la financiación de la adquisición de una vivienda (es decir, una hipoteca) O cualquier otro tipo de préstamo por motivos de:

- Raza o color de piel,
- Origen nacional,
- Religión,
- Género,
- Estado civil,
- Edad (con tal de que sea lo suficiente mayor como para celebrar un contrato),
- Ser beneficiario/a de ingresos de un programa de asistencia pública o
- Por haber hecho valer derechos protegidos bajo el acta de Protección de Crédito del Consumidor

LA AGENCIA QUE PODRÍA AYUDAR:

Oficina para la Protección Financiera del Consumidor (CFPB, por sus siglas en inglés).

    En Internet:
    https://www.consumerfinance.gov/es/enviar-una-queja/

    Por teléfono: (855) 411-2372

Si su reporte está relacionado con discriminación en instalaciones públicas, entre ellos hoteles, restaurantes, teatros y otros establecimientos de ocio, el fiscal general de su estado podría ayudarle.

N.B.: Puede haber plazos para la presentación de querellas relacionadas con discriminación en instalaciones públicas. Si usted cree haber sido víctima de discriminación, debe comunicarse cuanto antes con el fiscal general de su estado.

YO EXPERIMENTÉ...

Discriminación en instalaciones públicas (hoteles, restaurantes, teatros y establecimientos de ocio) por motivos de:

- Raza o color de piel,
- Religión u
- Origen nacional

LA AGENCIA QUE PODRÍA AYUDAR:

Fiscales Generales Estatales

    En Internet: www.usa.gov/state-attorney-general (solo en inglés)
    Por teléfono: (844) 872-4681

Además, es posible que el colegio de abogados de su estado o su oficina local de asistencia legal podrían ayudarle con este asunto.

PARA LOCALIZAR A...

Un abogado particular

UNA ORGANIZACIÓN QUE PODRÍA AYUDARLE:

American Bar Association [Colegio de Abogados de los Estados Unidos]

    En Internet:
    www.findlegalhelp.org (solo en inglés)

    Por teléfono: (800) 285-2221

PARA LOCALIZAR A...

Un abogado particular para personas de bajos ingresos

UNA ORGANIZACIÓN QUE PODRÍA AYUDARLE:

Legal Services Corporation [Corporación de Servicios Legales] (o Legal Aid Offices [Oficinas de Asistencia Legal])

    En Internet:
    www.lsc.gov/find-legal-aid (solo en inglés)

Cómo nos ha ayudado:

Su reporte nos ayudará a fomentar los derechos civiles. La información contenida en reportes como el suyo nos ayuda a entender asuntos emergentes y urgentes relacionados con los derechos civiles. Esto, a su vez, nos ayuda a informar cómo protegemos los derechos civiles de todas las personas en este país.

Gracias por comunicarse con el Departamento de Justicia acerca de sus preocupaciones.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)
    ResponseTemplate.objects.create(
        title='SPL - Referral for PREA Issues (Spanish)',
        subject=subject,
        body="""
{{ addressee }}:

Usted se comunicó con el Departamento de Justicia el {{ es.date_of_intake }}. Con base en nuestro repaso hasta la fecha, quisiéramos avisarle que tal vez quiera comunicarse con el Coordinador de la PREA [Ley contra la Violación en las Cárceles] de su estado.

Lo que hicimos:

Su número de registro es {{ record_locator }}.

Miembros del equipo de la División de Derechos Civiles revisaron la información que usted entregó. Con base en su reporte, nuestro equipo determinó que sus preocupaciones están relacionadas con abusos sexuales o acoso sexual estando en la cárcel. Esto podría ser amparado por la ley contra la Violación en las Cárceles (PREA). PREA es una ley que prohíbe:

- abusar sexualmente o acosar sexualmente a reclusos y detenidos o
- tomar represalias contra un recluso o miembro del personal que denuncie el abuso sexual o acoso sexual.

Seguiremos revisando su reporte y nos comunicaremos con usted si necesitamos alguna información adicional. No obstante, cabe destacar que en situaciones que conllevan el abuso sexual o acoso sexual de reclusos y detenidos, la División de Derechos Civiles solo podrá involucrarse cuando existe un patrón generalizado de mala conducta. Por lo tanto, por lo general, no podemos iniciar investigaciones basadas en alegaciones individuales.

En consecuencia, queremos avisarle que el Coordinador de la PREA de su estado podría ayudarle con su situación. Un Coordinador de la PREA puede investigar alegaciones individuales como la suya. Para facilitar su comunicación con el Coordinador de la PREA, hemos incluido un directorio con esta respuesta.

Lo que usted puede hacer:

El Coordinador de la PREA de su estado podría ayudarle con su situación. Para comunicarse con el Coordinador de la PREA de su estado, consulte el directorio adjunto.

Por otra parte, puede aprender más sobre PREA en el sitio web del Centro de Información sobre PREA: www.prearesourcecenter.org/training-technical-assistance/prea-101/prisons-and-jail-standards (solo en inglés)

Cómo nos ha ayudado:

Su reporte nos ayudará a fomentar los derechos civiles. La información contenida en reportes como el suyo nos ayuda a entender asuntos y tendencias emergentes relacionados con los derechos civiles. Esto, a su vez, nos ayuda a informar cómo protegemos los derechos civiles de todas las personas en este país.

Gracias por comunicarse con el Departamento de Justicia acerca de sus preocupaciones.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
        """)


def remove_spanish_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    templates = ResponseTemplate.objects.filter(title__icontains='(Spanish)')
    templates.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0090_district_add_65_and_90'),
    ]

    operations = [
        migrations.RunPython(add_spanish_templates, remove_spanish_templates)
    ]
