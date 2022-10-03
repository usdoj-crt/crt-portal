import time
from django.core.management.base import BaseCommand, CommandError
from cts_forms.models import Report, RepeatWriterInfo
from django.db import connection

class Command(BaseCommand):
    help = "Generates reports for each year of activity, stored in comma separated value format (.csv)."

    def handle(self, *args, **options):
        start = time.time()
        reports = Report.objects.all()
        total_email_count = 0
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM cts_forms_repeatwriterinfo;")
        for report in reports:
            if report.contact_email:
                repeat_writer = RepeatWriterInfo.objects.filter(email=report.contact_email).first()
                if repeat_writer:
                    repeat_writer.email_count = repeat_writer.email_count + 1
                    repeat_writer.save()
                else:
                    RepeatWriterInfo.objects.create(email=report.contact_email, email_count=1)
                    total_email_count += 1
        # Stop the timer:
        end = time.time()
        elapsed = round(end - start, 4)
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {total_email_count} repeat writer email counts in {elapsed} seconds.'))
