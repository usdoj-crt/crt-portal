"""Back end forms"""
import secrets

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ..forms import ComplaintActions, ReportEditForm
from ..model_variables import PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES
from ..models import CommentAndSummary, Report, HateCrimesandTrafficking
from .test_data import SAMPLE_REPORT


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


class ReportEditFormTests(TestCase):
    def setUp(self):
        self.report_data = SAMPLE_REPORT.copy()
        self.report_data.update({'primary_complaint': 'workplace',
                                 'public_or_private_employer': PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES[0][0]})
        self.report = Report.objects.create(**self.report_data)

    def test_changed_data_hatecrime(self):
        """If our hatecrime boolean was changed, hatecrimetrafficking must be in changed_data"""
        data = self.report_data.copy()
        data.update({'hatecrime': True})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertTrue('hatecrimes_trafficking' in form.changed_data)

    def test_changed_data_trafficking(self):
        """If our trafficking boolean was changed, hatecrimetrafficking must be in changed_data"""
        data = self.report_data.copy()
        data.update({'trafficking': True})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertTrue('hatecrimes_trafficking' in form.changed_data)

    def test_clean_hatecrime_trafficking_empty(self):
        """On final clean, hatecrimetrafficking must be set to combined values of hatecrime and trafficking booleans"""
        hatecrime, _ = HateCrimesandTrafficking.objects.get_or_create(value='physical_harm')
        trafficking, _ = HateCrimesandTrafficking.objects.get_or_create(value='trafficking')

        data = self.report_data.copy()
        data.update({'trafficking': False, 'hatecrime': False})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['hatecrimes_trafficking'], [])

        data.update({'trafficking': True, 'hatecrime': False})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['hatecrimes_trafficking'], [trafficking])

        data.update({'trafficking': False, 'hatecrime': True})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['hatecrimes_trafficking'], [hatecrime])

        data.update({'trafficking': True, 'hatecrime': True})
        form = ReportEditForm(data, instance=self.report)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['hatecrimes_trafficking'], [hatecrime, trafficking])

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
