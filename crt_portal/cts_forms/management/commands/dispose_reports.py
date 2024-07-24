from datetime import datetime

from django.core.management.base import BaseCommand
from cts_forms.model_variables import BATCH_APPROVED_STATUS, BATCH_ARCHIVED_STATUS
from cts_forms.models import ReportDispositionBatch


class Command(BaseCommand):
    help = 'Dispose of reports that have been approved for disposal.'

    def handle(self, *args, **options):

        disposable_batches = ReportDispositionBatch.objects.filter(
            status=BATCH_APPROVED_STATUS,
            proposed_disposal_date__lte=datetime.now()
        )

        for batch in disposable_batches:
            batch.redact_reports()
        batch.status = BATCH_ARCHIVED_STATUS
        batch.save()
