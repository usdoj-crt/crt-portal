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
    PURPOSE_CHOICES = [
        (AUTO_EMAIL, 'Autoresponse'),
        (MANUAL_EMAIL, 'Manual response'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tms_id = models.BigIntegerField(unique=True)
    report = models.ForeignKey('cts_forms.Report', related_name='emails', blank=True, on_delete=models.CASCADE)
    subject = models.TextField(help_text='Subject line of outbound email')
    body = models.TextField(help_text='Body of outbound email')
    recipient = models.EmailField()
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES, default=MANUAL_EMAIL)
    error_message = models.TextField(help_text='If failed, this field will contain any error messages provided by TMS', null=True)

    def __str__(self):
        return f"TMS messsage ID: {self.tms_id}"

    @property
    def failed(self):
        """True if this email attempt failed"""
        return self.status == TMSEmail.FAILED
