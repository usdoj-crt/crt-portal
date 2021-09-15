from django.db import migrations


def update_spanish_PREA(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    spanish_prea_form = ResponseTemplate.objects.get(title='SPL - Referral for PREA Issues (Spanish)')
    # adjust addressee and indentation
    spanish_prea_form.body = """
{{ es.addressee }}:

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

"""
    spanish_prea_form.save()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0122_auto_reply_form_letter'),
    ]

    operations = [
        migrations.RunPython(update_spanish_PREA)
    ]