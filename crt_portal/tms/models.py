from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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

    tms_id = models.BigIntegerField(unique=True)
    report = models.ForeignKey('cts_forms.Report', related_name='emails', blank=True, on_delete=models.CASCADE)
    recipient = models.EmailField()
    created_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)

    def __str__(self):
        return f"TMS messsage ID: {self.tms_id}"
