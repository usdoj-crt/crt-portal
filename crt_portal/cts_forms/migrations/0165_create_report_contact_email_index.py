from django.db import migrations
from django.db import connection

def create_report_contact_email_index(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS cts_forms_report_contact_email_idx
            ON public.cts_forms_report USING btree
            (contact_email)
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0164_create_actstream_description_index'),
    ]
    operations = [
        migrations.RunPython(create_report_contact_email_index)
    ]