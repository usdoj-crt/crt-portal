import time
import csv
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Prefetch
from cts_forms.models import Report, ReportsData, CommentAndSummary
from datetime import datetime
from io import StringIO
from django.core.files.base import ContentFile
from pytz import timezone

from ...admin import iter_queryset, _serialize_report_export

EXCLUDED_REPORT_FIELDS = ['violation_summary_search_vector', 'referral_section']
REPORT_FIELDS = [field.name for field in Report._meta.fields if field.name not in EXCLUDED_REPORT_FIELDS]


class Command(BaseCommand):  # pragma: no cover
    help = "Generates reports for each year of activity, stored in comma separated value format (.csv)."

    def handle(self, *args, **options):
        try:
            # For performance monitoring
            UTC = timezone('UTC')
            EST = timezone('America/New_York')
            start = time.time()
            year_range = list(range(2020, datetime.today().year + 1))
            total_count = 0
            # Create reports for each year
            for year in year_range:
                start_date = UTC.localize(datetime(year, 1, 1))
                end_date = UTC.localize(datetime(year, 12, 31, 23, 59, 59))
                filename = f'reports-data-{year}.csv'
                headers = REPORT_FIELDS + ['protected_class', 'internal_summary']
                summaries = CommentAndSummary.objects.filter(is_summary=True).order_by('-modified_date')
                queryset = Report.objects.all().filter(create_date__gte=start_date, create_date__lte=end_date)
                queryset = queryset.prefetch_related('protected_class',
                                                     Prefetch('internal_comments', queryset=summaries,
                                                              to_attr='internal_summary')
                                                     ).order_by('id')
                total_count += queryset.count()
                iterator = iter_queryset(queryset, headers)
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL)

                for report in iterator:
                    csv_writer.writerow(_serialize_report_export(report))
                csv_file = ContentFile(csv_buffer.getvalue().encode('utf-8'))
                # Check to see if a report of the given filename exists, if so, update.  If not, create a new one.
                try:
                    reports_data = ReportsData.objects.filter(filename=filename).first()
                    reports_data.file.save(filename, csv_file)
                    reports_data.filename = filename
                    reports_data.modified_date = EST.localize(datetime.now())
                    reports_data.save()
                except AttributeError:
                    reports_data = ReportsData.objects.create()
                    reports_data.file.save(filename, csv_file)
                    reports_data.filename = filename
                    reports_data.modified_date = EST.localize(datetime.now())
                    reports_data.save()

            # Stop the timer:
            end = time.time()
            elapsed = round(end - start, 4)

        except OSError as error:
            raise CommandError(f'Error writing CSV file: {error}')
        except ValueError as error:
            raise CommandError(f'Something went wrong: {error}')

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {total_count} reports in {elapsed} seconds.'))
