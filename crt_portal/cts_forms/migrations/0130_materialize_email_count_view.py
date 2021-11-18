from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0129_drs_hhs_referral_letter'),
    ]

    operations = [
        migrations.RunSQL("""
            DROP VIEW email_report_count;
        """),
        migrations.RunSQL("""
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
        """),
    ]
