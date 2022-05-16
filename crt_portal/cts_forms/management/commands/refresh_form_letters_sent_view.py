from django.core.management.base import BaseCommand
from cts_forms.models import FormLettersSent


class Command(BaseCommand):
    help = "Refreshes the Form Letters Sent materialized view"

    def handle(self, *args, **options):
        FormLettersSent.refresh_view()
