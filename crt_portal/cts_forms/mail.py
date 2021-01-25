from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def crt_send_mail(report, template):
    """
    Given a report and a template, use django's builtin `send_mail` to generate and send
    an outbound email
    """
    subject = template.render_subject(report)
    message = template.render_body(report)
    recipient_list = [report.contact_email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
    logger.info(f'Sent email response template #{template.id} to report: {report.id}')
