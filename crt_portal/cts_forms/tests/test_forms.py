"""Back end forms"""
import secrets

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils.html import escape

from ..forms import ComplaintActions, ReportEditForm
from ..model_variables import PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES
from ..models import CommentAndSummary, Report, ResponseTemplate
from .test_data import SAMPLE_REPORT, SAMPLE_RESPONSE_TEMPLATE


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
                kwargs={'report_id': self.pk},
            ),
            {
                'is_summary': False,
                'note': self.note,
                'next': '?per_page=15',
            },
            follow=True
        )

    def test_post(self):
        """A logged in user can post a comment"""
        self.assertEquals(self.response.status_code, 200)

    def test_retain_query(self):
        """if the user came to the page with query parameters, keep them for the back to all button."""
        self.assertTrue('?per_page=15' in str(self.response.content))

    def test_creates_comment(self):
        """A comment is created and associated with the right report"""
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        report = Report.objects.filter(internal_comments__pk=comment_id)[0]
        self.assertEquals(report.pk, self.pk)

    def test_adds_comment_to_activity(self):
        """The comment shows up in the report's activity log"""
        response = self.client.get(
            reverse(
                'crt_forms:crt-forms-show',
                kwargs={'id': self.pk}),
        )
        content = str(response.content)
        self.assertTrue(self.note in content)

    def test_edit_summary(self):
        comment_id = CommentAndSummary.objects.get(note=self.note).pk
        update = 'updated note'
        response = self.client.post(
            reverse(
                'crt_forms:save-report-comment',
                kwargs={'report_id': self.pk},
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


class ReportEditFormTests(TestCase):
    def setUp(self):
        self.report_data = SAMPLE_REPORT.copy()
        self.report_data.update({'primary_complaint': 'workplace',
                                 'public_or_private_employer': PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES[0][0]})
        self.report = Report.objects.create(**self.report_data)

    def test_changed_data_hate_crime(self):
        data = self.report_data.copy()
        data.update({'hate_crime': 'yes'})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertTrue('hate_crime' in form.changed_data)

    def test_clean_dependent_fields(self):
        """
        On clean, dependent fields of non-selected primary_complaint are set to ""
        Only fields previously containing values are included in changed_data
        """
        data = self.report_data.copy()
        new_primary_complaint = 'housing'
        data.update({'primary_complaint': new_primary_complaint})
        form = ReportEditForm(data, instance=self.report)

        self.assertTrue(form.is_valid())
        self.assertTrue('public_or_private_employer' in form.changed_data)
        self.assertTrue('employer_size' not in form.changed_data)
        for field in Report.PRIMARY_COMPLAINT_DEPENDENT_FIELDS['workplace']:
            self.assertTrue(form.cleaned_data[field] == "")

    def test_summary_can_be_created(self):
        """
        Saving of a valid form instance creates an associated
        CommentAndSummary object w/ is_summary is True
        """
        data = self.report_data.copy()
        new_summary = 'summarized'
        data.update({'summary': new_summary})
        form = ReportEditForm(data, instance=self.report)

        self.assertTrue(form.is_valid())
        self.assertTrue('summary' in form.changed_data)

        form.save()
        self.report.refresh_from_db()
        self.assertEqual(self.report.get_summary.note, new_summary)

    def test_summary_can_be_updated(self):
        """
        Saving of a valid form instance updates the associated
        CommentAndSummary object w/ is_summary is True
        """
        # Create and add a summary to our test report
        summary, _ = CommentAndSummary.objects.get_or_create(note='summary', is_summary=True)
        self.report.internal_comments.add(summary)

        data = self.report_data.copy()
        new_summary = 'newest summary'
        data.update({'summary': new_summary, 'summary_id': summary.id})
        form = ReportEditForm(data, instance=self.report)

        self.assertTrue(form.is_valid())
        self.assertTrue('summary' in form.changed_data)

        form.save()

        self.report.refresh_from_db()
        summary.refresh_from_db()
        self.assertEqual(self.report.get_summary.note, new_summary)
        self.assertEqual(summary.note, new_summary)

    def test_location_address_not_replaced(self):
        data = self.report_data.copy()
        data.update({
            'location_address_line_1': 'location address 1',
            'location_address_line_2': 'location address 2',
        })
        report = Report.objects.create(**data)
        form = ReportEditForm(data, instance=report)
        self.assertTrue(form.is_valid())
        fields = form.clean()
        self.assertFalse('location_address_line_1' in fields)
        self.assertFalse('location_address_line_2' in fields)


class ResponseActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)
        self.report = Report.objects.create(**SAMPLE_REPORT)
        self.template = ResponseTemplate.objects.create(**SAMPLE_RESPONSE_TEMPLATE)

    def post_template_action(self, what):
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'templates': self.template.id,
                'type': what,
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        return str(response.content)

    def test_response_action_print(self):
        content = self.post_template_action('print')
        # verify that next QP is preserved and activity log shows up
        self.assertTrue('?per_page=15' in content)
        self.assertTrue('Contacted complainant:' in content)
        self.assertTrue(escape(f"Printed '{self.template.title}' template") in content)

    def test_response_action_copy(self):
        content = self.post_template_action('copy')
        # verify that next QP is preserved and activity log shows up
        self.assertTrue('?per_page=15' in content)
        self.assertTrue('Contacted complainant:' in content)
        self.assertTrue(escape(f"Copied '{self.template.title}' template") in content)

    def test_response_action_blank_submit(self):
        response = self.client.post(
            reverse(
                'crt_forms:crt-forms-response',
                kwargs={'id': self.report.id},
            ),
            {
                'next': '?per_page=15',
            },
            follow=True
        )
        self.assertEquals(response.status_code, 200)
        content = str(response.content)
        self.assertTrue('?per_page=15' in content)
        self.assertFalse('Contacted complainant:' in content)
