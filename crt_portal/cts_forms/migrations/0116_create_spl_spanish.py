from django.db import migrations


def add_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    subject = 'Respuesta: Su informe de la División de Derechos Civiles - {{ record_locator }} de la Sección {{ es.section_name }}'
    ResponseTemplate.objects.create(
        title='SPL - Standard Form Letter (Spanish)',
        subject=subject,
        language='es',
        body="""
{{ es.addressee }},

Gracias por su carta del {{ es.date_of_intake }}. Su número de informe es {{ record_locator }} . Para la identificación de vulneraciones de derechos civiles, la Sección de Litigios Especiales depende de información de miembros de la comunidad. Cada semana, recibimos cientos de informes de posibles vulneraciones. Para elegir casos, recopilamos y analizamos estos datos, y a veces empleamos esta información como pruebas en un caso existente. Nosotros revisaremos su carta para determinar si debemos comunicarnos con usted para pedir información adicional. No disponemos de los recursos como para dar seguimiento a cada carta.

La Sección de Litigios Especiales es una de varias Secciones que forman parte de División de Derechos Civiles. Nuestro trabajo en la protección de derechos civiles se divide en cuatro áreas: 1) los derechos de personas que se encuentras en instituciones estatales o locales, entre ellos: cárceles, prisiones, centros de detención juvenil y establecimientos sanitarios para personas con discapacidades (incluyendo si personas en establecimientos sanitarios deben recibir servicios dentro de la comunidad en vez de en el establecimiento); 2) los derechos de personas que interactuan con la policía local o estatal o con algún departamento del alguacil; (3) los derechos de personas a tener acceso seguro a clínicas de atención médica reproductiva o a instituciones religiosas; y 4) los derechos de personas al libertad de culto en instituciones estatales y locales. No estamos habilitados para abordar problemas con instalaciones federales u oficiales federales. 

Si su motivo de preocupación no forma parte del área de trabajo de esta Sección, podría consultar la página web de la División de Derechos Civiles para localizar la sección correcta: https://civilrights.justice.gov/. 
 
La Sección de Litigios Especiales solamente se ocupa de casos que surgen de problemas generalizados que afectan a grupos de personas. No podemos ayudar con problemas individuales. No podemos ayudarle a recuperar daños o algún tipo de compensación personal. Tampoco podemos ayudar con casos penales, los que incluyen condenas injustas, apelaciones o sentencias. 


Si usted tiene un problema individual o está buscando una indemnización o algún otro tipo de compensación personal, puede consultar con un abogado particular o una organización de asistencia legal o sin ánimo de lucro para pedir ayuda. Existen solo dos áreas en las cuales podemos ayudar a un individuo u ocuparnos de un incidente individual: 1) es posible que podemos ayudarle si no le están permitiendo ejercer la libertad de culto en una prisión, una cárcel, un hospital de salud mental y otro establecimiento operado por o para un gobierno estatal o local; 2) es posible que podamos ayudarle si ha sido víctima de fuerza o la amenaza de fuerza al acceder a un centro de atención médica reproductiva o institución religiosa.
 
Para más información sobre la Sección de Litigios Especiales o el trabajo que realizamos, visite nuestra página web: www.justice.gov/crt/about/spl/.

Atentamente,

Departamento de Justicia de los EE. UU.
División de Derechos Civiles
""")


def remove_spl_standard_form_letters(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    templates = ResponseTemplate.objects.filter(title__icontains='SPL - Standard Form Letter (Spanish)')
    templates.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0115_spl_standard_form_letter'),
    ]

    operations = [
        migrations.RunPython(add_spl_standard_form_letters, remove_spl_standard_form_letters)
    ]