from django.db import migrations
from django.db import connection

def create_actstream_description_index(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS actstream_action_description_idx
            ON public.actstream_action USING btree
            (description)
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0163_crm_form_letters_update'),
    ]
    operations = [
        migrations.RunPython(create_actstream_description_index)
    ]