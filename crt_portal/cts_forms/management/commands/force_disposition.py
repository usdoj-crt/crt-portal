import os

from django.core.management.base import BaseCommand
from cts_forms.model_variables import BATCH_APPROVED_STATUS, BATCH_ARCHIVED_STATUS
from cts_forms.models import ReportDispositionBatch


class Command(BaseCommand):  # pragma: no cover
    help = "Ignore proposed disposal date and force disposal disposition batches"

    def handle(self, *args, **options):
        environment = os.environ.get('ENV', 'UNDEFINED')
        if environment not in ['LOCAL', 'UNDEFINED', 'STAGE', 'DEVELOP']:
            self.stdout.write(self.style.NOTICE(f'Cannot force disposition in {environment}'))
            return

        disposable_batches = ReportDispositionBatch.objects.filter(
            status=BATCH_APPROVED_STATUS,
        )

        for batch in disposable_batches:
            batch.redact_reports()
            batch.status = BATCH_ARCHIVED_STATUS
            batch.save()

        self.stdout.write(self.style.SUCCESS('Approved dispositions have been forced to Archived.'))
