from datetime import date
import time
import csv
from django.core.management.base import BaseCommand, CommandError
from cts_forms.models import Report

class Command(BaseCommand):
    help = "Generates reports for each year of activity, stored in comma separated value format (.csv)."

    def handle(self, *args, **options):
        # save output to db
        # match excel format - maybe need to test
        try:
            start = time.time()
            reports = Report.objects.all().filter(create_date__gte=date(2022,1,1), create_date__lte=date(2022,12,31))
            with open('2022.csv', 'wt') as csvfile:
                filewriter = csv.writer(csvfile, dialect='excel')
                for report in reports.values():
                    filewriter.writerow([report])
            end = time.time()
            elapsed = round(end - start, 4)
        except OSError:
            raise CommandError(f'Error writing CSV file: {OSError}')
        except ValueError:
            raise CommandError(f'Something went wrong: {ValueError}')

        self.stdout.write(self.style.SUCCESS(f'Successfully got all reports in {elapsed} seconds.'))
