from django.core.management.base import BaseCommand
from cts_forms.tests.factories import ReportFactory
from datetime import datetime
import random
from cts_forms.signals import salt
from cts_forms.models import EmailReportCount, ProtectedClass
from cts_forms.model_variables import PROTECTED_MODEL_CHOICES
from cts_forms.forms import add_activity
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create mock reports for local testing"

    forms = ['CRM R1 Form Letter',
             'CRM R2 Form Letter',
             'CRM - Referral to FBI',
             'CRT - Comments & Opinions',
             'CRT - Constant Writer',
             'CRT - EEOC Referral Letter',
             'CRT - No Capacity',
             'CRT - Non-Actionable',
             'CRT - Request for Agency Review',
             'DRS - Dept of Ed Referral Form Letter',
             'DRS - DOT Referral Form Letter',
             'DRS - EEOC Referral Form Letter',
             'DRS - HHS Referral Form Letter',
             'HCE - Form Letter',
             'IER - Form Letter',
             'SPL - Referral for PREA Issues',
             'SPL - Standard Form Letter',
             'Trending - General COVID inquiries',
             'EOS - Dept of Ed Referral Form Letter',
             'EOS - EEOC Referral Form Letter'
             ]

    # These are the probabilities that a given form letter will be sent.  I suspect we will adjust these after we see the
    # shape of production data.
    weights = [2, 1, 2, 2, 1, 2, 3, 16, 20, 4, 2, 1, 1, 1, 1, 1, 2, 3, 1, 2]

    def add_arguments(self, parser):
        parser.add_argument('number_reports')

    def handle(self, *args, **options):
        number_reports = int(options["number_reports"])
        random_form_letters = random.choices(population=self.forms, weights=self.weights, k=number_reports)  # nosec

        user1 = User.objects.filter(username="USER_1").first()
        if not user1:
            user1 = User.objects.create_user("USER_1", "user1@example.com", "")

        for i in range(number_reports):
            report = ReportFactory.build()
            report.create_date = datetime.now()
            # This save creates the report id, report.pk, so we can create a public_id
            report.save()
            salt_chars = salt()
            report.public_id = f'{report.pk}-{salt_chars}'
            report.intake_format = None
            report.public_id = ''
            # This code adds some frequent flier reports randomly to better emulate production
            # nosec turns off bandit error because random is not used for security or run outside of local env.
            rand = random.randint(1, 100)  # nosec
            # approximately 1% of reports
            if rand <= 1:
                report.contact_email = "frequentflier1@test.test"
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[0][0])
                protected_example3 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[2][0])
                protected_example4 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[3][0])
                protected_example5 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[4][0])
                report.protected_class.add(protected_example)
                report.protected_class.add(protected_example3)
                report.protected_class.add(protected_example4)
                report.protected_class.add(protected_example5)
            # 3%
            elif rand <= 3:
                report.contact_email = "frequentflier2@test.test"
                add_activity(user1, 'Contacted complainant:', f"Copied '{random_form_letters[i]}' template", report)
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[5][0])
                protected_example2 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[6][0])
                protected_example3 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[7][0])
                report.protected_class.add(protected_example)
                report.protected_class.add(protected_example2)
                report.protected_class.add(protected_example3)
            # 6%
            elif rand <= 6:
                report.contact_email = "frequentflier3@test.test"
                add_activity(user1, 'Contacted complainant:', f"Printed '{random_form_letters[i]}' template", report)
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[8][0])
                protected_example2 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[9][0])
                protected_example3 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[10][0])
                report.protected_class.add(protected_example)
                report.protected_class.add(protected_example2)
                report.protected_class.add(protected_example3)
            # 50% chance of sending an email
            elif rand <= 50:
                add_activity(user1, 'Contacted complainant:', f"Email sent: '{random_form_letters[i]}' to {report.contact_email} via govDelivery TMS", report)
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[0][0])
                report.protected_class.add(protected_example)
            report.save()
        EmailReportCount.refresh_view()
        self.stdout.write(self.style.SUCCESS(f'Created {number_reports} reports'))
