from django.db import migrations
from django.db import connection

def add_repeat_writer_view(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE MATERIALIZED VIEW repeat_writer_view AS
            select UPPER(contact_email) AS email, count(*)
            from cts_forms_report
            group by UPPER(contact_email);
        """)


def revert_repeat_writer_view(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP MATERIALIZED VIEW repeat_writer_view;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0155_repeatwriterinfo'),
    ]
    operations = [
        migrations.RunPython(add_repeat_writer_view, revert_repeat_writer_view)
    ]
