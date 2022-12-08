from django.core.management.base import BaseCommand
from cts_forms.models import RepeatSummaryInfo


class Command(BaseCommand):
    help = 'Refreshes the repeat_summary_view materialized view'

    def handle(self, *args, **options):
        RepeatSummaryInfo.refresh_view()
