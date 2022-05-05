from django.db import migrations, connection

def create_materialized_action_section_view(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE MATERIALIZED VIEW action_section AS
            SELECT report.public_id, report.contact_email, report.assigned_section, action.id, action.verb, action.description, action.target_object_id
            FROM cts_forms_report report
            JOIN actstream_action action
            ON report.public_id = action.target_object_id
        """)

class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0143_alter_report_district'),
    ]

    operations = [
        migrations.RunPython(create_materialized_action_section_view)
    ]