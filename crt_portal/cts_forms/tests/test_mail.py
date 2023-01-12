from cts_forms.mail import remove_disallowed_recipients
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from .test_data import SAMPLE_REPORT_1
from tms.models import TMSEmail
from ..models import Report


class CrtSendMailTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('tms:tms-webhook')
        self.email = TMSEmail.objects.create(
            tms_id='1234',
            created_at=timezone.now(),
            report=Report.objects.create(**SAMPLE_REPORT_1),
        )
        self.webhook_data = {
            'message_url': 'abc/1234'
        }

    def tearDown(self):
        self.email.delete()

    @override_settings(RESTRICT_EMAIL_RECIPIENTS_TO=['dev.test@test.com'])
    def test_remove_disallowed_recipients(self):
        """
        Targets for email messages are removed if the address is not found in
        the restricted recipients list
        """
        recipients = ['to1@example.com', 'dev.test@test.com']
        self.assertEqual(remove_disallowed_recipients(recipients), ['dev.test@test.com'])

        recipients = ['to1@example.com']
        self.assertEqual(remove_disallowed_recipients(recipients), [])

    @override_settings(RESTRICT_EMAIL_RECIPIENTS_TO=[])
    def test_dont_remove_disallowed_recipients_if_none(self):
        """
        Targets for email messages not modified if no restrictions
        """
        recipients = ['to1@example.com', 'to2@test.com']
        self.assertEqual(remove_disallowed_recipients(recipients), recipients)

    @override_settings(RESTRICT_EMAIL_RECIPIENTS_TO=['mixedCASE@example.com'])
    def test_case_remove_disallowed_recipients(self):
        """
        Test to make sure the correct restricted emails are used, regardless of case.
        """
        recipients = ['MiXedCAsE@example.com']
        self.assertEqual(remove_disallowed_recipients(recipients), ['MiXedCAsE@example.com'])

    @override_settings(TMS_WEBHOOK_ALLOWED_CIDR_NETS=['*'])
    def test_handles_empty_data_from_tms(self):
        self.client.post(self.webhook_url, {
            **self.webhook_data
        })

        self.email.refresh_from_db()
        self.assertEqual(self.email.status, TMSEmail.INCONCLUSIVE)
        self.assertEqual(self.email.error_message, 'Warning: This message may have sent, but was not marked as completed by TMS')

    @override_settings(TMS_WEBHOOK_ALLOWED_CIDR_NETS=['*'])
    def test_handles_errors_from_tms(self):
        self.client.post(self.webhook_url, {
            **self.webhook_data,
            'status': TMSEmail.FAILED,
            'error_message': 'oh no bad thing',
        })

        self.email.refresh_from_db()
        self.assertEqual(self.email.status, TMSEmail.FAILED)
        self.assertEqual(self.email.error_message, 'oh no bad thing')

    @override_settings(TMS_WEBHOOK_ALLOWED_CIDR_NETS=['*'])
    def test_handles_complete_data_from_tms(self):
        self.client.post(self.webhook_url, {
            **self.webhook_data,
            'status': TMSEmail.SENT,
            'completed_at': "2015-08-05 18:47:18 UTC",
        })

        self.email.refresh_from_db()
        self.assertEqual(self.email.status, TMSEmail.SENT)
        self.assertIsNone(self.email.error_message)
        self.assertEqual(self.email.completed_at.isoformat(), '2015-08-05T18:47:18+00:00')
