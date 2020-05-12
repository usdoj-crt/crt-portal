
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import Report
from ..model_variables import PRIMARY_COMPLAINT_CHOICES
from ..forms import ContactEditForm, ReportEditForm
from .test_data import SAMPLE_REPORT


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
