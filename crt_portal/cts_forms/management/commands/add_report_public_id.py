from django.core.management.base import BaseCommand, CommandError
from cts_forms.models import Report
from cts_forms.signals import salt


class Command(BaseCommand):
    help = 'Add public_id to reports without them.'

    def add_arguments(self, parser):
        parser.add_argument('report_pks', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        report_pks = kwargs['report_pks']
        print(report_pks)
        for report_pk in report_pks:
            print("report_pk", report_pk)
            try:
                report = Report.objects.get(pk=report_pk)
                print("report", report)
            except report.DoesNotExist:
                raise CommandError('Report "%s" does not exist' % report_pk)

            salt_chars = salt()
            if not report.public_id:
                report.public_id = f'{report.pk}-{salt_chars}'
                self.stdout.write(self.style.SUCCESS('Successfully write public_id to "%s"' % report_pk))
            if not report.intake_format:
                report.intake_format = 'web'
                self.stdout.write(self.style.SUCCESS('Successfully write intake_format to "%s"' % report_pk))
            report.save()
