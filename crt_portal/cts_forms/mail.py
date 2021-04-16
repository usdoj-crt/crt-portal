import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from tms.models import TMSEmail

logger = logging.getLogger(__name__)


def crt_send_mail(report, template):
    """
    Given a report and a template, use django's builtin `send_mail` to generate and send
    an outbound email
    """
    subject = template.render_subject(report)
    message = template.render_body(report)
    recipient_list = [report.contact_email]
    # We're only sending email to one recipient, we'll take the first and only response from the API
    response = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)[0]

    TMSEmail(tms_id=response['id'],
             recipient=report.contact_email,
             report=report,
             created_at=datetime.strptime(response['created_at'], '%Y-%m-%dT%H:%M:%S%z'),
             status=response['status']
             ).save()

    logger.info(f'Sent email response template #{template.id} to report: {report.id}')
