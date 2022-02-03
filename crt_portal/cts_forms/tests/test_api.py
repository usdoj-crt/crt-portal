"""
Internal views and misc views
"""
import copy
import io
import secrets
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from unittest.mock import patch
from django.shortcuts import get_object_or_404

from testfixtures import LogCapture

from ..forms import ContactEditForm, ReportEditForm, add_activity
from ..model_variables import PRIMARY_COMPLAINT_CHOICES
from ..models import Profile, Report, ReportAttachment, ProtectedClass, PROTECTED_MODEL_CHOICES, CommentAndSummary
from .test_data import SAMPLE_REPORT
from .factories import ReportFactory


class APIBaseUrlTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.url = reverse('api:api-base')

    def tearDown(self):
        self.user.delete()

    def test_api_base_url(self):
        """test api base url get status"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('/api/reports' in str(response.content))

    def test_unauthenticated_api_base_url(self):
        """test api base url not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/api/')

class APIReportListTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.url = reverse('api:report-list')

    def tearDown(self):
        self.user.delete()

    def test_report_list_url(self):
        """test report list get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        print("content is => ", str(response.content))
        self.assertTrue('/api/reports/1' in str(response.content))
        self.assertTrue('false' in str(response.content))

    def test_unauthenticated_report_list_url(self):
        """test report list not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTrue('Authentication credentials were not provided' in str(response.content))
        self.assertEqual(response.status_code, 403)


class APIReportDetailTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT)
        self.user = User.objects.create_user('DELETE_USER', 'george@thebeatles.com', '')
        self.client.login(username='DELETE_USER', password='')  # nosec
        self.url = reverse('api:report-detail', kwargs={'pk': self.test_report.pk})

    def tearDown(self):
        self.user.delete()

    def test_report_detail_url(self):
        """test report detail get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('false' in str(response.content))
        self.assertFalse('true' in str(response.content))

    def test_report_detail_mark_true_return_message(self):
        """test report detail post status"""
        response = self.client.post(self.url, {"viewed": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('true' in str(response.content))
        self.assertFalse('false' in str(response.content))

    def test_report_detail_mark_true_model_updated(self):
        """test report detail update model"""
        response = self.client.post(self.url, {"viewed": "true"})
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=self.test_report.id)
        first_activity = list(report.target_actions.all())[0]
        self.assertEqual(report.viewed, True)
        self.assertTrue("Report viewed:" in str(first_activity))

    def test_unauthenticated_report_detail_url(self):
        """test report detail not logged in"""
        self.client.logout()
        response = self.client.post(self.url, {"viewed": "true"})
        self.assertTrue('Authentication credentials were not provided' in str(response.content))
        self.assertEqual(response.status_code, 403)
