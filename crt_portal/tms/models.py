from datetime import datetime
import random
import uuid

from django.db import models


class TMSEmail(models.Model):
    """
    Tracking of outbound messages delivered to and tracked by the govDelivery TMS API
    """
    NEW = 'new'
    SENDING = 'sending'
    SENT = 'sent'
    FAILED = 'failed'
    INCONCLUSIVE = 'inconclusive'
    STATUS_CHOICES = [
        (NEW, 'New'),
        (SENDING, 'Sending'),
        (SENT, 'Sent'),
        (FAILED, 'Failed'),
        (INCONCLUSIVE, 'Inconclusive'),
    ]

    AUTO_EMAIL = 'auto'
    MANUAL_EMAIL = 'manual'
    NOTIFICATION = 'internal'
    PURPOSE_CHOICES = [
        (AUTO_EMAIL, 'Autoresponse'),
        (MANUAL_EMAIL, 'Manual response'),
        (NOTIFICATION, 'Internal notification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tms_id = models.BigIntegerField(unique=True)
    report = models.ForeignKey('cts_forms.Report', related_name='emails', blank=True, on_delete=models.CASCADE)
    subject = models.TextField(help_text='Subject line of outbound email')
    body = models.TextField(help_text='Body of outbound email')
    html_body = models.TextField(help_text='HTML body of outbound email, if present', null=True)
    recipient = models.EmailField()
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES, default=MANUAL_EMAIL)
    error_message = models.TextField(help_text='If failed, this field will contain any error messages provided by TMS', null=True)

    def __str__(self):
        return f"TMS messsage ID: {self.tms_id}"

    @classmethod
    def create_fake(cls, *, report, **kwargs):
        try:
            latest_id = cls.objects.latest('tms_id').tms_id + 1
        except cls.DoesNotExist:
            latest_id = 1

        status = random.choice([choice[0] for choice in cls.STATUS_CHOICES])  # nosec

        error_message = None
        if status == cls.FAILED:
            error_message = 'This is a fake error message'

        completed_at = None
        if status == cls.SENT:
            completed_at = datetime.now()

        return cls(tms_id=latest_id,
                   recipient=report.contact_email,
                   report=report,
                   created_at=datetime.now(),
                   completed_at=completed_at,
                   status=status,
                   error_message=error_message,
                   **kwargs)

    @property
    def sent_content(self):
        """The content that was actually (attempted to be) sent to the user."""
        return self.html_body or self.body

    @property
    def failed(self):
        """True if this email attempt failed"""
        return self.status == TMSEmail.FAILED
