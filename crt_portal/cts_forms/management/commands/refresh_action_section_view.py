from django.core.management.base import BaseCommand
from cts_forms.models import ActionSection


class Command(BaseCommand):
    help = "Refreshes the Action Section materialized view"

    def handle(self, *args, **options):
        ActionSection.refresh_view()
