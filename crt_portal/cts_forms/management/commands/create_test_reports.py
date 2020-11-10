from django.core.management.base import BaseCommand

from cts_forms.tests.factories import ReportFactory


class Command(BaseCommand):
    help = 'Create N reports with randomly generated data'

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Creating reports...'))
        report = ReportFactory.create_batch(5000)

        # self.stdout.write(self.style.SUCCESS(project.accounting_code.billable))
        # self.stdout.write(self.style.SUCCESS(rp))


        # self.stdout.write(self.style.SUCCESS('Successfully updated all timecards!'))
