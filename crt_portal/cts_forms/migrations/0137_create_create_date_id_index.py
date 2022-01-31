from django.db import migrations, models
from django.db import connection

def create_create_date_id_index(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS cts_forms_id_create_date_idx
            ON public.cts_forms_report USING btree
            (create_date ASC NULLS LAST, id ASC NULLS LAST)
        """)

def revert_create_date_id_index(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP INDEX cts_forms_id_create_date_idx
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0136_auto_20211216_1433'),
    ]
    operations = [
        migrations.RunPython(create_create_date_id_index, revert_create_date_id_index)
    ]

