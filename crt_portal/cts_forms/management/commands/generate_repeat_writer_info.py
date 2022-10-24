from django.core.management.base import BaseCommand
from cts_forms.models import RepeatWriterInfo


class Command(BaseCommand):
    help = 'Refreshes the repeat_writer_view materialized view'

    def handle(self, *args, **options):
        RepeatWriterInfo.refresh_view()
