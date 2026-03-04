from django.core.management.base import BaseCommand
from cts_forms.tests.factories import EmailFactory
from zoneinfo import ZoneInfo
from datetime import datetime, timezone


class Command(BaseCommand):  # pragma: no cover
    help = "Create a single TMS Email for local testing"

    def handle(self, *args, **options):
        email = EmailFactory.build()
        email.created_at = datetime.now(timezone.utc)
        email.completed_at = datetime.now(timezone.utc)
        email.save()
        self.stdout.write(self.style.SUCCESS('Created a TMS email entry'))
