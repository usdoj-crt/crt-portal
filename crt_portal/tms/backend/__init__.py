from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from tms.api.client import TMSClient
import logging

logger = logging.getLogger()


class TMSEmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the calls and responses to the TMS API
    """

    EMAIL_ENDPOINT = "/messages/email"

    def __init__(
        self, api_root=None, api_auth_token=None, fail_silently=False, **kwargs
    ):
        super().__init__(fail_silently=fail_silently)
        self.api_root = api_root or settings.TMS_TARGET_ENDPOINT
        self.api_auth_token = api_auth_token or settings.TMS_AUTH_TOKEN
        self.connection = None

    def open(self):
        """
        Create a TMSClient instance
        """
        if self.connection:
            return False
        try:
            self.connection = TMSClient(
                api_root=self.api_root, api_auth_token=self.api_auth_token
            )
        except Exception:
            if not self.fail_silently:
                raise

    def close(self):
        """
        No persistent connection to handle but we'll remove any APIClient instances
        """
        self.connection = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return responses from TMS API
        """
        messages_sent = []
        self.open()
        for message in email_messages:
            response = self._send(message)
            if response:
                messages_sent.append(response)
        return messages_sent

    def _prepare_outbound_dict(self, email_message):
        """
        Establish outbound payload for TMS send email POST API
        """
        recipients = [{"email": to_address} for to_address in email_message.to]
        return {
            "subject": email_message.subject,
            "body": email_message.body,
            "recipients": recipients,
            "open_tracking_enabled": False,
            "click_tracking_enabled": False,
        }

    def _remove_disallowed_recipients(self, email_message):
        """
        If we've limited the recipients, modify the `to` attribute of our email_message
        """
        # If the list of restrictions is empty, allow all
        restricted_to = settings.RESTRICT_EMAIL_RECIPIENT_DOMAINS_TO
        if restricted_to:
            email_message.to = [
                to_address
                for to_address in email_message.to
                if to_address.split("@")[1] in restricted_to
            ]
        return email_message

    def _send(self, email_message):
        """
        A helper method that does the actual sending.
        """
        outbound_message = self._remove_disallowed_recipients(email_message)
        if not outbound_message.recipients():
            return {}
        outbound_data = self._prepare_outbound_dict(outbound_message)
        response = self.connection.post(target=self.EMAIL_ENDPOINT, payload=outbound_data)

        if response.status_code == 201:
            # Success per TMS docs
            logger.debug(
                f"TMS API email success:<{response.status_code}> {response.json()}"
            )
        else:
            logger.warn(
                f"TMS API email send failed:<{response.status_code}> {response.json()}"
            )
            if not self.fail_silently:
                raise
        return response.json()
