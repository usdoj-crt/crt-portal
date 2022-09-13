from datetime import date, timezone
import time
import csv
from django.core.management.base import BaseCommand, CommandError
from cts_forms.models import Report, ReportsData
from datetime import datetime
import requests
from django.urls import reverse
from django.core.files import File
from django.core.files.base import ContentFile
import io

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
            # Open file:
            # with open('2022.csv', 'wt') as csvfile:
            #     filewriter = csv.writer(csvfile, dialect='excel')
            #     # Write reports to file:
            #     for report in reports.values():
            #         filewriter.writerow([report])
            # # Write to database
            # f = open('2022.csv')
            # reports_data_csv = File(f)
            # print(reports_data_csv)
            # myfile = ContentFile("hello world")
            # ReportsData.objects.create(file=reports_data_csv, created_date=datetime.now())
            requests.post(
                reverse(
                    'crt_forms:save-report-data',
                ),
                {
                    'file': io.StringIO('this is a fake file'),
                    'created_date': datetime.now()
                },
            )
            # Stop the timer:
            end = time.time()
            elapsed = round(end - start, 4)
        except OSError:
            raise CommandError(f'Error writing CSV file: {OSError}')
        except ValueError:
            raise CommandError(f'Something went wrong: {ValueError}')

        self.stdout.write(self.style.SUCCESS(f'Successfully got all reports in {elapsed} seconds.'))

#
# from datetime import date, datetime
# import time
# import csv
# from django.core.management.base import BaseCommand, CommandError
# from cts_forms.models import Report, ReportsData, CommentAndSummary
# from django.http import HttpResponse
# from django.core.files.base import ContentFile
# from cts_forms.admin import Echo, REPORT_FIELDS
# from django.http import StreamingHttpResponse
#
#
# class Command(BaseCommand):
#     help = "Generates reports for each year of activity, stored in comma separated value format (.csv)."
#
#     def _serialize_report_export(data):
#         """
#         Customize the rendering of protected_class and summary instances
#         while rendering headers as-is
#         """
#         if isinstance(data, Report):
#             row = [getattr(data, field) for field in REPORT_FIELDS]
#             row.append('; '.join([str(pc) for pc in data.protected_class.all()]))
#             # if data.internal_summary:
#             #     # incoming summaries are sorted by descending modified_date the first is the most recent
#             #     row.append(data.internal_summary[0].note)
#             # else:
#             #     row.append('')
#             return row
#         return data
#
#     def handle(self, *args, **options):
#         """
#         Stream all non-related fields,
#         protected_class M2M,
#         and latest summary from CommentAndSummary M2M of selected reports as a CSV
#         Log all use
#         """
#         writer = csv.writer(Echo(), quoting=csv.QUOTE_ALL)
#         headers = REPORT_FIELDS + ['protected_class', 'internal_summary']
#
#         # summaries = CommentAndSummary.objects.filter(is_summary=True).order_by('-modified_date')
#         # queryset = queryset.prefetch_related('protected_class',
#         #                                      Prefetch('internal_comments', queryset=summaries,
#         #                                               to_attr='internal_summary')
#         #                                      ).order_by('id')
#         # iterator = iter_queryset(queryset, headers)
#         reports = Report.objects.all()
#
#         response = StreamingHttpResponse((writer.writerow(self._serialize_report_export(report)) for report in reports),
#                                          content_type="text/csv")
#         response['Content-Disposition'] = 'attachment; filename="reports-2020.csv"'
#         # logger.info(format_export_message(request, queryset.count(), 'reports'))
#         # return response
#         # except OSError:
#         #     raise CommandError(f'Error writing CSV file: {OSError}')
#         # except ValueError:
#         #     raise CommandError(f'Something went wrong: {ValueError}')
#         #
#         # # self.stdout.write(self.style.SUCCESS(f'Successfully got all reports in {elapsed} seconds.'))
#
#  # def handle(self, *args, **options):
#  #        # save output to db
#  #        # match excel format - need to test
#  #        try:
#  #            # For performance monitoring, we'll start a little timer:
#  #            start = time.time()
#  #            # reports = Report.objects.all().filter(create_date__gte=date(2022,1,1), create_date__lte=date(2022,12,31))
#  #            reports = Report.objects.all()
#  #            # Set up for saving to db
#  #            # Might need a user for permissions
#  #            # Might need an http verb
#  #            report_csv = ReportsData
#  #            print("ReportsData", ReportsData)
#  #            # Create the HttpResponse object with the appropriate CSV header.
#  #            response = HttpResponse(
#  #                content_type='text/csv',
#  #                headers={'Content-Disposition': 'attachment; filename="reports-2020.csv"'},
#  #            )
#  #            writer = csv.writer(response)
#  #            for report in reports.values():
#  #                writer.writerow([report])
#  #            report_csv.file = response
#  #            report_csv.filename = "reports-2020.csv"
#  #            report_csv.created_date = datetime.now()
#  #            report_csv.save()
#  #
#  #            print("writer", writer)
#  #            print("report_csv", report_csv)
#  #            # Open file:
#  #            # with open('2022.csv', 'wt') as csvfile:
#  #            #     filewriter = csv.writer(csvfile, dialect='excel')
#  #            #     # Write reports to file:
#  #            #     for report in reports.values():
#  #            #         filewriter.writerow([report])
#  #            #     # Write to database
#  #            #     attachment.file = csvfile
#  #            #     attachment.filename = '2022'
#  #            #     attachment.created_date = datetime.now()
#  #            #     attachment.save()
#  #            # # Stop the timer:
#  #            # end = time.time()
#  #            # elapsed = round(end - start, 4)
#  #        except OSError:
#  #            raise CommandError(f'Error writing CSV file: {OSError}')
#  #        except ValueError:
#  #            raise CommandError(f'Something went wrong: {ValueError}')
#  #
#  #        # self.stdout.write(self.style.SUCCESS(f'Successfully got all reports in {elapsed} seconds.'))
