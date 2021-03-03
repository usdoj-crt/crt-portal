import io
import secrets

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from unittest.mock import patch

from ..forms import ContactEditForm, ReportEditForm
from ..model_variables import PRIMARY_COMPLAINT_CHOICES
from ..models import Profile, Report, ReportAttachment
from .test_data import SAMPLE_REPORT
from .factories import ReportFactory


class ProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        sample_profile = {
            'intake_filters': 'ADM',
            'user_id': self.user.id
        }
        self.test_profile = Profile.objects.create(**sample_profile)
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.form_data = {'type': 'profile_form'}
        self.url = reverse('crt_forms:cts-forms-profile')

    def tearDown(self):
        self.user.delete()

    def test_profile_form_save(self):
        """Profile create on successfull POST"""
        new_intake_filters = ['VOT', 'ADM']
        self.form_data.update({'intake_filters': new_intake_filters})
        self.client.post(self.url, self.form_data, follow=True)
        self.test_profile.refresh_from_db()
        self.assertEqual(self.test_profile.intake_filters, 'VOT,ADM')


class ContactInfoUpdateTests(TestCase):

    def setUp(self):
        self.test_report = Report.objects.create(**SAMPLE_REPORT)
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.form_data = {'type': ContactEditForm.CONTEXT_KEY}

        self.url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.test_report.id})

    def tearDown(self):
        self.user.delete()

    def test_update_name_and_zipcode(self):
        """Contact info updates on successfull POST"""
        new_first_name = 'TESTER'
        new_zipcode = '00000'
        self.form_data.update({'contact_first_name': new_first_name})
        self.form_data.update({'contact_zip': new_zipcode})
        response = self.client.post(self.url, self.form_data, follow=True)
        self.assertTrue(response.context['data'].contact_first_name == new_first_name)

        self.test_report.refresh_from_db()
        self.assertEqual(self.test_report.contact_first_name, new_first_name)
        self.assertEqual(self.test_report.contact_zip, new_zipcode)

    def test_no_update_if_validation_fails(self):
        """Contact info not updated if form validation fails
            errors rendered on resulting page
        """
        new_email = 'not an email'
        original_email = self.test_report.contact_email
        self.form_data.update({'contact_email': new_email})
        response = self.client.post(self.url, self.form_data, follow=True)

        self.test_report.refresh_from_db()
        self.assertEqual(self.test_report.contact_email, original_email)

        # Error message rendered on page
        self.assertContains(response, ContactEditForm.FAIL_MESSAGE)


class ReportEditShowViewTests(TestCase):

    def setUp(self):
        self.report_data = SAMPLE_REPORT.copy()
        self.report_data.update({'primary_complaint': PRIMARY_COMPLAINT_CHOICES[0][0]})
        self.report = Report.objects.create(**self.report_data)
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec

        self.url = reverse('crt_forms:crt-forms-show', kwargs={'id': self.report.id})

    def tearDown(self):
        self.user.delete()

    def test_returns_400_if_no_formtype(self):
        """400 error returned if form_type is missing"""
        form_data = {}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 400)

    def test_update_primary_cause(self):
        """Report fields update on successfull POST"""
        new_primary_complaint = PRIMARY_COMPLAINT_CHOICES[1][0]
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'primary_complaint': new_primary_complaint}
        response = self.client.post(self.url, form_data, follow=True)

        self.report.refresh_from_db()
        self.assertEqual(self.report.primary_complaint, new_primary_complaint)
        self.assertTrue(response.context['data'].primary_complaint == new_primary_complaint)

    def test_excluded_fields_not_modifiable(self):
        """If form data is received outside of scope of ReportEditForm it's not saved"""
        # Contact info
        initial_summary = self.report.violation_summary
        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'violation_summary': 'test'}
        response = self.client.post(self.url, form_data, follow=True)

        self.report.refresh_from_db()
        self.assertTrue(response.context['data'].violation_summary == initial_summary)

    def test_only_keep_errors_from_submitted_form(self):
        """If invalid form data is received for multiple forms
           Only report errors for submitted form
           Discard other data

           Here we submit an invalid ReportEditForm, w/ month out of range
           and include post data for a contact information field.

           The resulting rendered page must contain a new ContactEditForm
           and not contain the submitted contact_email data
        """
        initial = self.report.contact_email

        form_data = {'type': ReportEditForm.CONTEXT_KEY, 'last_incident_month': 99, 'contact_email': 'test@'}
        response = self.client.post(self.url, form_data, follow=True)

        self.assertEqual(response.context['contact_form'].initial['contact_email'], initial)


class CRTReportWizardTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('crt_report_form')

    @override_settings(MAINTENANCE_MODE=True)
    def test_returns_503_when_maintenance_mode_true(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 503)

    def test_returns_200_when_maintenance_mode_false(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ReportAttachmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.report = ReportFactory.create()
        self.pk = self.report.pk
        self.fake_file = io.StringIO('this is a fake file')
        self.test_pass = secrets.token_hex(32)
        self.user = User.objects.create_user('DELETE_USER', 'ringo@thebeatles.com', self.test_pass)
        self.client.login(username='DELETE_USER', password=self.test_pass)

    @patch('cts_forms.models.ReportAttachment.full_clean')
    def test_post_valid_file(self, mock_validate_file_infection):
        response = self.client.post(
            reverse(
                'crt_forms:save-report-attachment',
                kwargs={'report_id': self.pk}
            ),
            {
                'report': self.pk,
                'file': self.fake_file
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('Successfully attached file' in str(response.content))

    @patch('cts_forms.models.ReportAttachment.full_clean')
    def test_post_invalid_file(self, mock_validate_file_infection):
        mock_validate_file_infection.side_effect = ValidationError('invalid file')
        response = self.client.post(
            reverse(
                'crt_forms:save-report-attachment',
                kwargs={'report_id': self.pk}
            ),
            {
                'report': self.pk,
                'file': self.fake_file
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('Could not save attachment: invalid file' in str(response.content))

    def test_get_attachment(self):
        user_specified_filename = 'a'
        internal_filename = 'b'

        file = TemporaryUploadedFile(internal_filename, 'text/plain', 10000, 'utf-8')
        attachment = ReportAttachment.objects.create(file=file, user=self.user, filename=user_specified_filename, report=self.report)
        attachment.save()

        response = self.client.get(
            reverse(
                'crt_forms:get-report-attachment',
                kwargs={'id': self.pk, 'attachment_id': attachment.pk}
            ),
        )

        # we should reply with a redirect to a presigned s3 url
        self.assertEqual(response.status_code, 302)
        # the presigned url should target the private S3 bucket
        self.assertTrue('/crt-private/' in str(response.url))
        # the presigned url should have a 30 second expiration
        self.assertTrue('Expires=30' in str(response.url))
        # the presigned url should target the internal (not user specified) filename
        self.assertTrue(f'/attachments/{internal_filename}' in str(response.url))
        # the response-content-disposition should be set so that the file downloads with the user specified filename
        self.assertTrue(f'response-content-disposition=attachment%3Bfilename%3D{user_specified_filename}' in str(response.url))
