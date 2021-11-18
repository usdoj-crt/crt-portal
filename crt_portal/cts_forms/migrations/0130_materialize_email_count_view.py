from django.db import migrations, models
from django.db import connection

def change_email_count_view_to_materialized(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP VIEW email_report_count;
        """)
        cursor.execute("""
            CREATE MATERIALIZED VIEW email_report_count AS
                    WITH email_counts AS (
                                SELECT UPPER(cts_forms_report_1.contact_email) AS email,
                        count(*) AS email_count
                    FROM cts_forms_report cts_forms_report_1
                    GROUP BY UPPER(cts_forms_report_1.contact_email)
                    )
            SELECT cts_forms_report.id AS report_id,
                email_counts.email_count
            FROM cts_forms_report
                LEFT JOIN email_counts ON UPPER(cts_forms_report.contact_email) = UPPER(email_counts.email);
        """)
        cursor.execute("""
            CREATE UNIQUE INDEX on public.email_report_count ( report_id );
        """)


def revert_email_count_view(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            DROP INDEX email_report_count_report_id_idx
        """)
        cursor.execute("""
            DROP MATERIALIZED VIEW email_report_count;
        """)
        cursor.execute("""
            CREATE OR REPLACE VIEW email_report_count AS
                    WITH email_counts AS (
                                SELECT UPPER(cts_forms_report_1.contact_email) AS email,
                        count(*) AS email_count
                    FROM cts_forms_report cts_forms_report_1
                    GROUP BY UPPER(cts_forms_report_1.contact_email)
                    )
            SELECT cts_forms_report.id AS report_id,
                email_counts.email_count
            FROM cts_forms_report
                LEFT JOIN email_counts ON UPPER(cts_forms_report.contact_email) = UPPER(email_counts.email);
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0129_drs_hhs_referral_letter'),
    ]
    operations = [
        migrations.RunPython(change_email_count_view_to_materialized, revert_email_count_view)
    ]

