from django.core.management.base import BaseCommand
from cts_forms.models import FormLettersSent
from cts_forms.tests.factories import ReportFactory
from datetime import datetime
from pytz import timezone
import random
from cts_forms.signals import salt
from cts_forms.models import EmailReportCount, ProtectedClass
from cts_forms.model_variables import PROTECTED_MODEL_CHOICES, DISTRICT_CHOICES
from cts_forms.forms import add_activity
from django.contrib.auth.models import User
from random import randrange
from datetime import timedelta


SECTIONS = ['ADM', 'APP', 'CRM', 'DRS', 'ELS', 'EOS', 'FCS', 'HCE', 'IER', 'POL', 'SPL', 'VOT']

def random_dist():
    district_arr = []
    for district_choice in DISTRICT_CHOICES:
        district_arr.append(district_choice[0])
    return random.choice(district_arr)

def random_date():
    """
    This function will return a random datetime between two datetime
    objects.
    """
    UTC = timezone('UTC')
    start_date = UTC.localize(datetime(2020, 1, 1))
    end_date = UTC.localize(datetime.now())
    delta = end_date - start_date
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)  # nosec
    return start_date + timedelta(seconds=random_second)


class Command(BaseCommand):  # pragma: no cover
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
             'CRT - Dept of Ed Referral Form Letter',
             'CRT - DOT Referral Form Letter',
             'CRT - EEOC Referral Form Letter',
             'CRT - HHS Referral Form Letter',
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
        user2 = User.objects.filter(username="USER_2").first()
        if not user2:
            user2 = User.objects.create_user("USER_2", "user1@example.com", "")
        user3 = User.objects.filter(username="USER_3").first()
        if not user3:
            user3 = User.objects.create_user("USER_3", "user1@example.com", "")

        for i in range(number_reports):
            report = ReportFactory.build()
            UTC = timezone('UTC')
            date = random_date()
            report.save()
            report.create_date = date
            salt_chars = salt()
            report.public_id = f'{report.pk}-{salt_chars}'

            # Code to replicate bad data that can occur in prod when there are database errors.
            # report.intake_format = None
            # report.public_id = ''

            # This code adds some frequent flier reports randomly to better emulate production
            # nosec turns off bandit error because random is not used for security or run outside of local env.
            rand = random.randint(1, 100)  # nosec
            # approximately 1% of reports
            if rand <= 1:
                add_activity(user1, 'Contacted complainant:', "frequentflier1@test.test not in allowed domains, not attempting to deliver CRT Auto response.", report)
                report.contact_email = "frequentflier1@test.test"
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[0][0])
                protected_example3 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[2][0])
                protected_example4 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[3][0])
                protected_example5 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[4][0])
                report.protected_class.add(protected_example)
                report.protected_class.add(protected_example3)
                report.protected_class.add(protected_example4)
                report.protected_class.add(protected_example5)
                report.create_date = UTC.localize(datetime(2020, 6, 21, 18, 25, 30))
                if report.assigned_section != 'CRM':
                    add_activity(user1, 'Assigned section:', f'Updated from "{report.assigned_section}" to "CRM"', report)
                    report.assigned_section = 'CRM'
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
                report.create_date = UTC.localize(datetime(2021, 12, 31, 18, 25, 30))
                if report.assigned_section != 'SPL':
                    add_activity(user1, 'Assigned section:', f'Updated from "{report.assigned_section}" to "SPL"', report)
                    report.assigned_section = 'SPL'
            # 6%
            elif rand <= 6:
                report.contact_email = "frequentflier3@test.test"
                add_activity(user2, 'Contacted complainant:', f"Printed '{random_form_letters[i]}' template", report)
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[8][0])
                protected_example2 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[9][0])
                protected_example3 = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[10][0])
                report.protected_class.add(protected_example)
                report.protected_class.add(protected_example2)
                report.protected_class.add(protected_example3)
                report.create_date = UTC.localize(datetime(2021, 1, 1, 0, 0, 0))
                if report.assigned_section != 'VOT':
                    add_activity(user2, 'Assigned section:', f'Updated from "{report.assigned_section}" to "VOT"', report)
                    report.assigned_section = 'VOT'
            # 50% chance of sending an email
            elif rand <= 50:
                if report.assigned_section != 'DRS':
                    add_activity(user3, 'Assigned section:', f'Updated from "{report.assigned_section}" to "DRS"', report)
                    report.assigned_section = 'DRS'
                add_activity(user3, 'Contacted complainant:', f"Email sent: '{random_form_letters[i]}' to {report.contact_email} via govDelivery TMS", report)
                add_activity(user3, 'Contacted complainant:', f"Email sent: '{random_form_letters[i]}' to {report.contact_email} via govDelivery TMS", report)
                add_activity(user3, 'Contacted complainant:', f"Email sent: '{random_form_letters[i]}' to {report.contact_email} via govDelivery TMS", report)
                add_activity(user3, 'Contacted complainant:', f"Email sent: '{random_form_letters[i]}' to {report.contact_email} via govDelivery TMS", report)
                add_activity(user3, 'Contacted complainant:', f"Email sent: '{random_form_letters[i]}' to {report.contact_email} via govDelivery TMS", report)
                protected_example = ProtectedClass.objects.get(value=PROTECTED_MODEL_CHOICES[0][0])
                report.protected_class.add(protected_example)
                report.district = random_dist()
            elif rand <= 70:
                referral = random.choice(SECTIONS)  # nosec
                if report.assigned_section != referral:
                    add_activity(user3, 'Assigned section:', f'Updated from "{report.assigned_section}" to "{referral}"', report)
                    report.assigned_section = referral
            report.save()
        EmailReportCount.refresh_view()
        FormLettersSent.refresh_view()
        self.stdout.write(self.style.SUCCESS(f'Created {number_reports} reports'))
