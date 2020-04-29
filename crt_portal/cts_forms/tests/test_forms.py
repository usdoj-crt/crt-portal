"""Back end forms"""
import secrets

from django.test import SimpleTestCase, TestCase
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import User

from ..forms import ComplaintActions
from ..models import Report, CommentAndSummary
from .test_data import SAMPLE_REPORT


class ComplaintActionTests(SimpleTestCase):
    def setUp(self):
        self.form = ComplaintActions()

    def test_get_actions_returns_verb_and_description_for_each_changed_field(self):
        self.form.changed_data = ['field_test']
        self.form.cleaned_data = {'field_test': 'verb'}
        actions = [action for action in self.form.get_actions()]
        self.assertEqual(actions, [("updated field test", " to verb")])


class ActionTests(TestCase):
    def test_valid(self):
        form = ComplaintActions(data={
            'assigned_section': 'ADM',
            'status': 'new',
            'primary_statute': '144',
            'district': '1',
        })
        self.assertTrue(form.is_valid())


class CommentActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # we are not running the tests against the production database, so this shouldn't be producing real users anyway.
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

        self.note = 'Important note'
        self.report = Report.objects.create(**SAMPLE_REPORT)
        self.pk = self.report.pk
        self.response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': self.pk}
            ),
            {
                'is_summary': False,
                'note': self.note,
            },
            follow=True
        )

    def test_post(self):
        """A logged in user can post a comment"""
        self.assertEquals(self.response.status_code, 200)

    def test_creates_comment(self):
        """A comment is created and associated with the right report"""
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        report = Report.objects.filter(internal_comments__pk=comment_id)[0]
        self.assertEquals(report.pk, self.pk)

    def test_adds_comment_to_activity(self):
        """The comment shows up in the report's activity log"""
        response = self.client.get(
            reverse('crt_forms:crt-forms-show', kwargs={'id': self.pk})
        )
        content = str(response.content)
        self.assertTrue(self.note in content)

    def test_edit_summary(self):
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        update = 'updated note'
        response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': self.pk}
            ),
            {
                'is_summary': False,
                'note': update,
                'comment_id': comment_id,
            },
            follow=True
        )
        content = str(response.content)
        self.assertTrue('updated note' in content)
