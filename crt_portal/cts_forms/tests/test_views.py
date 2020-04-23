
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import Report
from ..forms import ContactEditForm
from .test_data import SAMPLE_REPORT


class ContactInfoUpdateTests(TestCase):

    def setUp(self):
        self.test_report = Report.objects.create(**SAMPLE_REPORT)
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')
        self.form_data = {'type': 'contact-info'}

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
