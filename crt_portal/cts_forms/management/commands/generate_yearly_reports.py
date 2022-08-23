from datetime import date, datetime
import time
import csv
from django.core.management.base import BaseCommand, CommandError
from cts_forms.models import Report, ReportsData

class Command(BaseCommand):
    help = "Generates reports for each year of activity, stored in comma separated value format (.csv)."

    def handle(self, *args, **options):
        # save output to db
        # match excel format - need to test
        try:
            # For performance monitoring, we'll start a little timer:
            start = time.time()
            reports = Report.objects.all().filter(create_date__gte=date(2022,1,1), create_date__lte=date(2022,12,31))
            # Set up for saving to db
            # Might need a user for permissions
            # Might need an http verb
            attachment = ReportsData
            # Open file:
            with open('2022.csv', 'wt') as csvfile:
                filewriter = csv.writer(csvfile, dialect='excel')
                # Write reports to file:
                for report in reports.values():
                    filewriter.writerow([report])
                # Write to database
                attachment.file = csvfile
                attachment.filename = '2022'
                attachment.created_date = datetime.now()
                attachment.save()
            # Stop the timer:
            end = time.time()
            elapsed = round(end - start, 4)
        except OSError:
            raise CommandError(f'Error writing CSV file: {OSError}')
        except ValueError:
            raise CommandError(f'Something went wrong: {ValueError}')

        self.stdout.write(self.style.SUCCESS(f'Successfully got all reports in {elapsed} seconds.'))
