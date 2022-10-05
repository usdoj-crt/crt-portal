import random
import string

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from .test_data import SAMPLE_REPORT_1, SAMPLE_REPORT_2, SAMPLE_REPORT_3, SAMPLE_REPORT_4
from ..models import Report, RepeatWriterInfo
from ..forms import add_activity


class CreateMockReports(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("DELETE_USER", "ringo@thebeatles.com", "")
        # Create 100 reports that all have the same violation summary
        for _ in range(100):
            Report.objects.create(**SAMPLE_REPORT_1)
        # Create one report that doesn't have the identical violation summary
        report_with_email = Report.objects.create(**SAMPLE_REPORT_2)
        repeat_writer1 = SAMPLE_REPORT_2["contact_email"]
        # send a constant writer email to the email associated with the report created above
        add_activity(self.user, "Contacted complainant:", f"Email sent: 'CRT - Constant Writer' to {repeat_writer1} via govDelivery TMS", report_with_email)
        # create 50 reports that were by the user who already received the repeat writer email and that have distinct violation summaries
        letters = string.ascii_lowercase
        for _ in range(50):
            SAMPLE_REPORT_2["violation_summary"] = ''.join(random.choice(letters) for i in range(10))
            SAMPLE_REPORT_2["contact_email"] = repeat_writer1
            Report.objects.create(**SAMPLE_REPORT_2)
        # Create another report with a new violation summary
        report_with_template = Report.objects.create(**SAMPLE_REPORT_4)
        repeat_writer2 = SAMPLE_REPORT_4["contact_email"]
        add_activity(self.user, "Contacted complainant:", "Printed 'CRT - Constant Writer' template", report_with_template)
        # create 50 reports that were by the user who had a Constant Writer template printed for their report and that have distinct violation summaries
        for _ in range(50):
            SAMPLE_REPORT_4["violation_summary"] = ''.join(random.choice(letters) for i in range(10))
            SAMPLE_REPORT_4["contact_email"] = repeat_writer2
            Report.objects.create(**SAMPLE_REPORT_4)

    def test_flag_repeat_writers_only_email_actions(self):
        flagged_reports = Report.objects.filter(by_repeat_writer=True).count()
        self.assertEqual(flagged_reports, 0)
        call_command('flag_repeat_writers')
        flagged_reports = Report.objects.filter(by_repeat_writer=True).count()
        self.assertEqual(flagged_reports, 202)

    def test_flag_repeat_writers_for_49_reports(self):
        for _ in range(48):
            Report.objects.create(**SAMPLE_REPORT_3)
        flagged_reports = Report.objects.filter(by_repeat_writer=True).count()
        self.assertEqual(flagged_reports, 0)
        call_command('flag_repeat_writers')
        flagged_reports = Report.objects.filter(by_repeat_writer=True).count()
        self.assertEqual(flagged_reports, 202)


class GenerateRepeatWriterInfo(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("DELETE_USER", "ringo@thebeatles.com", "")
        # Create 100 reports that all have the same violation summary
        self.email1 = SAMPLE_REPORT_1["contact_email"]
        self.email2 = SAMPLE_REPORT_2["contact_email"]
        self.email3 = SAMPLE_REPORT_3["contact_email"]
        self.email4 = SAMPLE_REPORT_4["contact_email"]
        for _ in range(100):
            Report.objects.create(**SAMPLE_REPORT_1)
        for _ in range(50):
            Report.objects.create(**SAMPLE_REPORT_2)
        for _ in range(50):
            Report.objects.create(**SAMPLE_REPORT_3)
        Report.objects.create(**SAMPLE_REPORT_4)
        call_command('generate_repeat_writer_info')

    def test_total_rows(self):
        repeat_writer_rows = RepeatWriterInfo.objects.all().count()
        self.assertEqual(repeat_writer_rows, 4)

    def test_email_count(self):
        repeat_writer_1 = RepeatWriterInfo.objects.filter(email=self.email1.lower()).first()
        self.assertEqual(repeat_writer_1.email_count, 100)
        repeat_writer_2 = RepeatWriterInfo.objects.filter(email=self.email2.lower()).first()
        self.assertEqual(repeat_writer_2.email_count, 50)
        repeat_writer_3 = RepeatWriterInfo.objects.filter(email=self.email3.lower()).first()
        self.assertEqual(repeat_writer_3.email_count, 50)
        repeat_writer_4 = RepeatWriterInfo.objects.filter(email=self.email4.lower()).first()
        self.assertEqual(repeat_writer_4.email_count, 1)

    def test_update_repeat_writer_info(self):
        for _ in range(5):
            Report.objects.create(**SAMPLE_REPORT_1)
        repeat_writer_1 = RepeatWriterInfo.objects.filter(email=self.email1.lower()).first()
        self.assertEqual(repeat_writer_1.email_count, 100)
        call_command('generate_repeat_writer_info')
        repeat_writer_1 = RepeatWriterInfo.objects.filter(email=self.email1.lower()).first()
        self.assertEqual(repeat_writer_1.email_count, 105)
