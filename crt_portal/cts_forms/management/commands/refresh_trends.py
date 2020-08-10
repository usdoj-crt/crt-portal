from django.core.management.base import BaseCommand
from cts_forms.models import Trends
import time


class Command(BaseCommand):
    help = 'Refreshes the Trends materialized view'

    def handle(self, *args, **options):
        start = time.time()
        Trends.refresh_view()
        end = time.time()
        elapsed = round(end - start, 4)

        self.stdout.write(self.style.SUCCESS(f'SUCCESS: Refreshed Trends view in {elapsed} seconds'))
