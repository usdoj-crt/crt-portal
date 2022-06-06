import random
import string

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from .test_data import SAMPLE_REPORT_1, SAMPLE_REPORT_2, SAMPLE_REPORT_3
from ..models import Report
from ..forms import add_activity


class CreateMockReports(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("DELETE_USER", "ringo@thebeatles.com", "")
        # Create 100 reports that all have the same violation summary
        for _ in range(100):
            Report.objects.create(**SAMPLE_REPORT_1)
        # Create one report that doesn't have the identical violation summary
        self.repeat_writer_report = Report.objects.create(**SAMPLE_REPORT_2)
        repeat_writer = SAMPLE_REPORT_2["contact_email"]
        # send a constant writer email to the email associated with the report created above
        add_activity(self.user, "Contacted complainant:", f"Email sent: 'CRT - Constant Writer' to {repeat_writer} via govDelivery TMS", self.repeat_writer_report)
        # create 50 reports that were by the user who already received the repeat writer email and that have distinct violation summaries
        letters = string.ascii_lowercase
        for _ in range(50):
            violation_summary = ''.join(random.choice(letters) for i in range(10))
            SAMPLE_REPORT_3["violation_summary"] = violation_summary
            SAMPLE_REPORT_3["contact_email"] = repeat_writer
            Report.objects.create(**SAMPLE_REPORT_3)

    def test_flag_repeat_writers_only_email_actions(self):
        flagged_reports = Report.objects.filter(by_repeat_writer=True).count()
        self.assertEqual(flagged_reports, 0)
        call_command('flag_repeat_writers')
        flagged_reports = Report.objects.filter(by_repeat_writer=True).count()
        self.assertEqual(flagged_reports, 151)
