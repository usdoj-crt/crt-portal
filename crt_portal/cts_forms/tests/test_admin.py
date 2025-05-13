import csv

from actstream.models import Action
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from shortener.models import ShortenedURL

from ..admin import ACTION_FIELDS, REPORT_FIELDS
from ..forms import add_activity
from ..models import Campaign, Report
from .test_data import SAMPLE_REPORT_1
from .factories import ReportFactory, UserFactory

User = get_user_model()


class ActionAdminTests(TestCase):

    def setUp(self):
        # We'll need a report and a handful of actions
        self.client = Client()
        self.superuser = User.objects.create_superuser('ACTION_EXPORT_TEST_USER', 'a@a.com', '')
        self.report = Report.objects.create(**SAMPLE_REPORT_1)
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

    def test_actor_filter(self):
        self.client.force_login(self.superuser)
        user1 = UserFactory.create_user("USER_1", "user1@example.com", "")
        user2 = UserFactory.create_user("USER_2", "user1@example.com", "")
        add_activity(user1, 'verb', 'Action 1', self.report)
        add_activity(user2, 'verb', 'Action 2', self.report)
        url1 = self.url
        url2 = self.url + f'?actor_object_id={user1.pk}'
        url3 = self.url + f'?actor_object_id={user2.pk}'
        response1 = self.client.get(url1)
        # show everything
        self.assertTrue('Action 1' in str(response1.content))
        self.assertTrue('Action 2' in str(response1.content))
        # filter on user1
        response2 = self.client.get(url2)
        self.assertTrue('Action 1' in str(response2.content))
        self.assertTrue('Action 2' not in str(response2.content))
        # filter on user2
        response3 = self.client.get(url3)
        self.assertTrue('Action 1' not in str(response3.content))
        self.assertTrue('Action 2' in str(response3.content))


class CampaignAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('CAMPAIGN_TEST_USER', 'a@a.com', '')
        self.client.force_login(self.superuser)
        if ShortenedURL.objects.first():
            ShortenedURL.objects.delete()
        if Campaign.objects.first():
            Campaign.objects.delete()

    def test_list(self):
        campaign = Campaign.objects.create(internal_name='Test Campaign')
        campaign.save()
        campaign.refresh_from_db()
        uuid = campaign.uuid

        target = reverse('admin:cts_forms_campaign_changelist')
        response = self.client.get(target)
        body = response.content.decode('utf-8')

        self.assertIn('<td class="field-internal_name">Test Campaign</td>', body)
        self.assertIn(('/admin/shortener/shortenedurl/add/?'
                       f'destination=/report?utm_campaign={uuid}'),
                      body)

    def test_list_with_url(self):
        campaign = Campaign.objects.create(internal_name='Test Campaign')
        campaign.save()
        campaign.refresh_from_db()
        uuid = campaign.uuid
        url = ShortenedURL.objects.create(
            shortname='test',
            destination=f'/report?utm_campaign={uuid}')
        short_url = url.get_short_url()

        target = reverse('admin:cts_forms_campaign_changelist')
        response = self.client.get(target)
        body = response.content.decode('utf-8')

        self.assertIn('<td class="field-internal_name">Test Campaign</td>', body)
        self.assertIn((f'<input aria-label="Short URL" disabled="disabled" class="admin-copy absolute-url" value="{short_url}"/>'), body)


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
