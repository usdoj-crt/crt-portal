from django.core.management.base import BaseCommand
from cts_forms.tests.factories import ReportFactory
from datetime import datetime
import random
from cts_forms.signals import salt
from cts_forms.models import EmailReportCount


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

            # This code adds some frequent flier reports randomly to better emulate production
            rand = random.randint(1, 100)
            # approximately 1% of reports
            if rand <= 1:
                report.contact_email = "frequentflier1@test.test"
            # 2%
            elif rand <= 3:
                report.contact_email = "frequentflier2@test.test"
            # 3%
            elif rand <= 6:
                report.contact_email = "frequentflier3@test.test"
            report.status = 'open'
            report.create_date = datetime.now()
            report.save()
            salt_chars = salt()
            report.public_id = f'{report.pk}-{salt_chars}'
            report.save()
        EmailReportCount.refresh_view()
        self.stdout.write(self.style.SUCCESS(f'Created {number_reports} reports'))
