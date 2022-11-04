from django.core.management.base import BaseCommand
from cts_forms.tests.factories import EmailFactory


class Command(BaseCommand):  # pragma: no cover
    help = "Create a single TMS Email for local testing"

    def handle(self, *args, **options):
        EmailFactory.create()
        self.stdout.write(self.style.SUCCESS('Created a TMS email entry'))
