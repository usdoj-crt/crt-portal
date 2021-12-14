from django.core.management.base import BaseCommand
from cts_forms.tests.factories import ReportFactory
from datetime import datetime
from cts_forms.signals import salt


class Command(BaseCommand):
    help = "Create mock reports for local testing"

    def add_arguments(self, parser):
        parser.add_argument('number_reports')

    def handle(self, *args, **options):
        number_reports = int(options["number_reports"])
        for i in range(number_reports):
            report = ReportFactory.build()
            # Uncomment the following line to create reports with the same email address
            # Note could will be useful for testing the "Total #" column in the form/view table
            # report.contact_email = "test@test.test"
            report.status = 'open'
            report.create_date = datetime.now()
            report.save()
            salt_chars = salt()
            report.public_id = f'{report.pk}-{salt_chars}'
            report.save()
        self.stdout.write(self.style.SUCCESS(f'Created {number_reports} reports'))
