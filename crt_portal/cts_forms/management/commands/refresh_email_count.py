from django.core.management.base import BaseCommand
from cts_forms.models import EmailReportCount


class Command(BaseCommand):
    help = 'Refreshes the Trends materialized view'

    def handle(self, *args, **options):
        EmailReportCount.refresh_view()
