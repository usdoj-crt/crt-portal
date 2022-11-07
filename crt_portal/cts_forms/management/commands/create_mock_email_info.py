from django.core.management.base import BaseCommand
from cts_forms.tests.factories import EmailFactory
from pytz import timezone
from datetime import datetime


class Command(BaseCommand):  # pragma: no cover
    help = "Create a single TMS Email for local testing"

    def handle(self, *args, **options):
        email = EmailFactory.build()
        UTC = timezone('UTC')
        email.created_at = UTC.localize(datetime.now())
        email.completed_at = UTC.localize(datetime.now())
        email.save()
        self.stdout.write(self.style.SUCCESS('Created a TMS email entry'))
