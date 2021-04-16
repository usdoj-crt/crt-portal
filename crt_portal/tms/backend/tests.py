from django.test import SimpleTestCase, override_settings
from django.core.mail import EmailMessage

from ..api.client import TMSClient
from . import TMSEmailBackend


class TMSEmailBackendTests(SimpleTestCase):

    def setUp(self):
        self.backend = TMSEmailBackend()

    def test_open_connection_is_a_tms_client(self):
        """Connection used for sending emails is a TMSClient instance"""
        self.backend.open()
        self.assertTrue(isinstance(self.backend.connection, TMSClient))

    @override_settings(RESTRICT_EMAIL_RECIPIENT_DOMAINS_TO=['test.com'])
    def test__remove_disallowed_recipients(self):
        """
        Targets for email messages are removed if the domain is not found in
        the recipients list
        """
        email = EmailMessage('Subject',
                             'Body',
                             'from@example.com',
                             ['to1@example.com', 'to2@test.com'],
                             )
        processed_email = self.backend._remove_disallowed_recipients(email)
        self.assertEquals(processed_email.to, ['to2@test.com'])
