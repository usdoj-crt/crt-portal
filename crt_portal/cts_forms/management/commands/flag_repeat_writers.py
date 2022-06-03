from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Flag reports that were submitted by repeat writers."

    def handle(self, *args, **options):
        # Flag reports that have the same violation summary as at least 50 reports
        repeat_summary_sql = """
        WITH repeat_summary AS (SELECT violation_summary, COUNT(*)
        FROM cts_forms_report 
        GROUP BY violation_summary
        HAVING count(*) > 50 )
        UPDATE cts_forms_report
        SET by_repeat_writer = true
        WHERE id IN
        (SELECT report.id
        FROM cts_forms_report report
        JOIN repeat_summary
        ON report.violation_summary = repeat_summary.violation_summary
        ORDER BY report.violation_summary);
        """

        cursor = connection.cursor()
        cursor.execute(repeat_summary_sql)

        # Flag reports that were submitted by individuals whose contact email addresses had already received a repeat writer email
        repeat_writer_sql = """
        UPDATE cts_forms_report 
        SET by_repeat_writer = true
        WHERE id IN (SELECT id
        FROM cts_forms_report report
        WHERE report.id IN (SELECT act.target_object_id::INTEGER
        FROM actstream_action act
        WHERE act.verb = 'Contacted complainant:'
        AND act.description LIKE '%Constant Writer%'));
        """

        cursor = connection.cursor()
        cursor.execute(repeat_writer_sql)