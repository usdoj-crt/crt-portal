"""
DRF API Tests
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from ..models import Report, ResponseTemplate
from .test_data import SAMPLE_REPORT_1, SAMPLE_RESPONSE_TEMPLATE
from cts_forms.views import add_activity
from actstream.models import actor_stream
from datetime import datetime


class APIBaseUrlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:api-base")

    def tearDown(self):
        self.user.delete()

    def test_api_base_url(self):
        """test api base url get status"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("/api/reports" in str(response.content))

    def test_unauthenticated_api_base_url(self):
        """test api base url not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/api/")


class APIFormLettersIndex(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:form-letters")

    def tearDown(self):
        self.user.delete()

    def test_form_letters_index(self):
        """test api endpoint called without an assigned section"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_form_letters"], 0)
        self.assertEqual(response.data["total_autoresponses"], 0)

    def test_unauthenticated_report_list_url(self):
        """test form letters index not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)


class APIPreviewResponseFormTests(TestCase):
    def setUp(self):
        self.client = Client(raise_request_exception=False)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.url = reverse("api:preview-response-form")

    def tearDown(self):
        self.user.delete()

    def test_help_page_renders(self):
        """Makes sure our route for previewing markdown files works."""
        self.client.login(username="DELETE_USER", password="")  # nosec

        response = self.client.get(self.url)

        self.assertContains(response, 'This page explains')

    def test_preview_response_text(self):
        """Makes sure our route for previewing markdown files works."""
        self.client.login(username="DELETE_USER", password="")  # nosec

        response = self.client.post(
            self.url,
            {"body": "hello, {{ addressee }}"}
        )

        self.assertContains(response, 'hello, <span class="variable">Addressee Name</span>')

    def test_preview_response_html(self):
        """Makes sure our route for previewing markdown files works."""
        self.client.login(username="DELETE_USER", password="")  # nosec

        response = self.client.post(
            self.url,
            {"body": "hello, *{{ addressee }}*", "is_html": True}
        )

        self.assertContains(response, 'hello, <em><span class="variable">Addressee Name</span></em>')

    def test_unauthenticated_post(self):
        """Only logged in users should be able to preview templates."""
        self.client.logout()

        response = self.client.post(self.url, {'body': 'oops'}, follow=True)

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_get(self):
        """Only logged in users should be able to preview templates."""
        self.client.logout()

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 403)


class APIPreviewResponseFileTests(TestCase):
    def setUp(self):
        self.client = Client(raise_request_exception=False)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")

    def tearDown(self):
        self.user.delete()

    def test_preview_response_text(self):
        """Makes sure our route for previewing markdown files works."""
        self.url = reverse(
            "api:preview-response-file",
            kwargs={"filename": 'crt_non_actionable.md'})
        self.client.login(username="DELETE_USER", password="")  # nosec

        response = self.client.get(self.url)

        self.assertContains(response, "Thank you for taking the time")
        self.assertContains(response, '<span class="variable">Addressee Name</span>')

    def test_preview_response_html(self):
        """Makes sure our route for previewing markdown files works."""
        self.url = reverse(
            "api:preview-response-file",
            kwargs={"filename": 'hce_form_letter.md'})
        self.client.login(username="DELETE_USER", password="")  # nosec

        response = self.client.get(self.url)

        self.assertContains(response, "Thank you for contacting")
        self.assertContains(response, '<span class="variable">Addressee Name</span>')
        self.assertContains(response, "<h1")

    def test_unauthenticated(self):
        """Only logged in users should be able to preview templates."""
        self.url = reverse(
            "api:preview-response-file",
            kwargs={"filename": 'crt_non_actionable.md'})
        self.client.logout()

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 403)


class APIReportListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:report-list")

    def tearDown(self):
        self.user.delete()

    def test_report_list_url(self):
        """test report list get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("/api/reports" in str(response.content))
        self.assertTrue("false" in str(response.content))

    def test_unauthenticated_report_list_url(self):
        """test report list not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)


class APIReportDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:report-detail", kwargs={"pk": self.test_report.pk})

    def tearDown(self):
        self.user.delete()

    def test_report_detail_url(self):
        """test report detail get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("false" in str(response.content))
        self.assertFalse("true" in str(response.content))

    def test_report_detail_mark_true_return_message(self):
        """test report detail post status"""
        response = self.client.post(self.url, {"viewed": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("true" in str(response.content))
        self.assertFalse("false" in str(response.content))

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
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)


class APIResponseListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:response-list")

    def tearDown(self):
        self.user.delete()

    def test_response_list_url(self):
        """test response list get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("/api/responses" in str(response.content))
        self.assertTrue("false" in str(response.content))

    def test_unauthenticated_response_list_url(self):
        """test response list not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)


class APIResponseDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:response-detail", kwargs={"pk": 1})

    def tearDown(self):
        self.user.delete()

    def test_response_detail_url(self):
        """test response detail get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "false")
        self.assertContains(response, "{{ addressee }}")

    def test_response_detail_url_with_report_id(self):
        """test response detail get with report_id"""
        response = self.client.get(self.url + f"?report_id={self.test_report.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "false")
        self.assertContains(response, "Lincoln")
        self.assertFalse("{{ addressee }}" in str(response.content))
        self.assertFalse("{{ record_locator }}" in str(response.content))
        self.assertFalse("{{ section_name }}" in str(response.content))
        self.assertFalse("{{ date_of_intake }}" in str(response.content))

    def test_unauthenticated_response_detail_url(self):
        """test response detail not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)


class APIReportsAccessedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report2 = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report3 = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:report-count") + "?intake_specialist=DELETE_USER"
        self.url2 = reverse("api:report-count") + "?start_date=2020-02-01&end_date=2022-04-01&intake_specialist=DELETE_USER"
        self.template = ResponseTemplate.objects.create(**SAMPLE_RESPONSE_TEMPLATE)

    def tearDown(self):
        self.user.delete()

    def test_report_count_url_without_arguments(self):
        """test report detail get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('"report_count":0' in str(response.content))

    def test_report_count_url_no_results(self):
        """test report detail get"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('"report_count":0' in str(response.content))

    def test_report_count_url_with_results(self):
        """test report detail get"""
        description = "Printed 'CRT - Request for Agency Review' template"
        add_activity(self.user, "Printed report", description, self.test_report)
        add_activity(self.user, "Printed report", description, self.test_report2)
        add_activity(self.user, "Printed report", description, self.test_report3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('"report_count":3' in str(response.content))

    def test_report_count_url_with_date_results(self):
        """test report detail get"""
        description = "Printed 'CRT - Request for Agency Review' template"
        add_activity(self.user, "Printed report", description, self.test_report)
        add_activity(self.user, "Printed report", description, self.test_report2)
        add_activity(self.user, "Printed report", description, self.test_report3)
        first_action = actor_stream(self.user).first()
        first_action.timestamp = datetime(2021, 1, 1)
        first_action.save()
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('"report_count":1' in str(response.content))

    def test_unauthenticated_report_detail_url(self):
        """test report detail not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)


class APIRelatedReportsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_report1 = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report2 = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report3 = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report4 = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report5 = Report.objects.create(**SAMPLE_REPORT_1)
        self.test_report6 = Report.objects.create(**SAMPLE_REPORT_1)
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.client.login(username="DELETE_USER", password="")  # nosec
        self.url = reverse("api:related-reports") + "?email=Lincoln@usa.gov"

    def tearDown(self):
        self.user.delete()

    def test_api_base_url(self):
        """test api base url get status"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_api_base_url(self):
        """test api base url not logged in"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_no_email_address(self):
        """if no email address provided the whole thing doesn't explode"""
        self.url = reverse("api:related-reports")
        response = self.client.get(self.url)
        self.assertTrue('count' in str(response.content))
        self.assertTrue('next' in str(response.content))
        self.assertTrue('previous' in str(response.content))
        self.assertTrue('results' in str(response.content))

    def test_number_of_results(self):
        """does the email address queried return a number equal to the number of reports created?"""
        self.client.login(username="DELETE_USER", password="")
        response = self.client.get(self.url)
        # We expect the count to equal the number of reports created:
        self.assertTrue('"count":6' in str(response.content))

    def test_returned_fields(self):
        """are all of the expected fields present in the response body?"""
        response = self.client.get(self.url)
        self.assertTrue('count' in str(response.content))
        self.assertTrue('next' in str(response.content))
        self.assertTrue('previous' in str(response.content))
        self.assertTrue('results' in str(response.content))
        self.assertTrue('pk' in str(response.content))
        self.assertTrue('viewed' in str(response.content))
        self.assertTrue('public_id' in str(response.content))
        self.assertTrue('assigned_section' in str(response.content))
        self.assertTrue('recent_email_sent' in str(response.content))
        self.assertTrue('create_date' in str(response.content))
        self.assertTrue('email' in str(response.content))


class APIResponseActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("DELETE_USER", "george@thebeatles.com", "")
        self.test_report = Report.objects.create(**SAMPLE_REPORT_1)
        self.template = ResponseTemplate.objects.create(**SAMPLE_RESPONSE_TEMPLATE)
        self.url = reverse("api:response-action")

    def tearDown(self):
        self.user.delete()

    def test_referral_response(self):
        """Makes sure our route for sending referral emails works."""
        self.client.login(username="DELETE_USER", password="")  # nosec
        response = self.client.post(
            self.url,
            {"report_id": self.test_report.pk, "template_id": self.template.pk, "action": "send"}
        )
        self.assertTrue(
            "email template" in str(response.content, 'utf-8')
        )

    def test_unauthenticated_referral_response_url(self):
        """test report detail not logged in"""
        self.client.logout()
        response = self.client.post(
            self.url,
            {"report_id": self.test_report.pk, "template_id": self.template.pk, "action": "send"}
        )
        self.assertTrue(
            "Authentication credentials were not provided" in str(response.content)
        )
        self.assertEqual(response.status_code, 403)
