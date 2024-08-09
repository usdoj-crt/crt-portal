import os
from django.core.management.base import BaseCommand
from cts_forms.models import ReportDisposition, ReportDispositionBatch, Report


class Command(BaseCommand):  # pragma: no cover
    help = "Reset the disposition objects on dev or staging for testing"

    def handle(self, *args, **options):
        environment = os.environ.get('ENV', 'UNDEFINED')
        if environment not in ['LOCAL', 'UNDEFINED', 'STAGE', 'DEVELOP']:
            self.stdout.write(self.style.NOTICE(f'Cannot reset disposition in {environment}'))
            return

        # They'll still be redacted, but if we don't undisposed them they'll give errors when linking to the disposition batch.
        reports = Report.all_objects.filter(disposed=True)
        reports.update(disposed=False)
        Report.objects.bulk_update(reports, ['disposed'])

        ReportDisposition.objects.all().delete()
        ReportDispositionBatch.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Disposition objects have been reset. Note that reports will still be redacted'))
