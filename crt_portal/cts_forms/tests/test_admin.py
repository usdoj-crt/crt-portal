import csv

from actstream.models import Action
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ..admin import ACTION_FIELDS, REPORT_FIELDS
from ..forms import add_activity
from ..models import Report
from .test_data import SAMPLE_REPORT
from .factories import ReportFactory

User = get_user_model()


class ActionAdminTests(TestCase):

    def setUp(self):
        # We'll need a report and a handful of actions
        self.client = Client()
        self.superuser = User.objects.create_superuser('ACTION_EXPORT_TEST_USER', 'a@a.com', '')
        self.report = Report.objects.create(**SAMPLE_REPORT)
        self.url = reverse('admin:actstream_action_changelist')

        [add_activity(self.superuser, 'verb', 'description', self.report) for _ in range(5)]

    def test_action_csv_export(self):
        """
        Selecting Actions and triggering the `export_actions_as_csv`
        action returns a StreamingHttpResponse containing a csv file
        with headers and all selected actions
        """
        self.client.force_login(self.superuser)
        form_data = {'action': 'export_actions_as_csv',
                     '_selected_action': [action.id for action in Action.objects.all()]}
        response = self.client.post(self.url, form_data)
        # Read through the entire streamed response
        rows = [r.decode('utf-8') for r in response.streaming_content]

        # Parse the response as a csv
        reader = csv.reader(rows)
        exported_action_csv = [row for row in reader]

        # Headers + 5 actions expected
        self.assertEqual(len(exported_action_csv), 6)

        # Headers match ACTION_FIELDS
        self.assertEqual(exported_action_csv[0], ACTION_FIELDS)


class ReportAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('REPORT_EXPORT_TEST_USER', 'a@a.com', '')
        self.url = reverse('admin:cts_forms_report_changelist')

        ReportFactory.create_batch(5)

    def test_report_csv_export(self):
        self.client.force_login(self.superuser)
        form_data = {'action': 'export_reports_as_csv',
                     '_selected_action': [report.id for report in Report.objects.all()]}

        response = self.client.post(self.url, form_data)

        # Read through the entire streamed response
        rows = [r.decode('utf-8') for r in response.streaming_content]

        reader = csv.reader(rows)
        exported_reports_csv = [row for row in reader]

        expected_header = REPORT_FIELDS + ['protected_class', 'internal_summary']

        self.assertEqual(exported_reports_csv[0], expected_header)
