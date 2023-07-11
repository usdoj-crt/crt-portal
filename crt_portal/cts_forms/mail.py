import logging
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
# bandit flags ANY import from ElementTree, not just parse-related ones.
# Element is not a parser and there is no alternative to importing from `xml`.
from xml.etree.ElementTree import Element  # nosec
from datetime import datetime
from django.shortcuts import get_object_or_404

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Report
from tms.models import TMSEmail

logger = logging.getLogger(__name__)


def remove_disallowed_recipients(recipient_list):
    """
    If we've limited the recipients, modify the `to` attribute of our email_message
    """
    # If the list of restrictions is empty, allow all
    restricted_to = settings.RESTRICT_EMAIL_RECIPIENTS_TO
    if restricted_to:
        recipient_list = [
            to_address
            for to_address in recipient_list
            if to_address.lower() in [email.lower() for email in restricted_to]
        ]
    return recipient_list


class CustomHTMLProcessor(Treeprocessor):
    # Alter the HTML output to provide inline styles and other custom markup.
    # For more, see here: https://github.com/Python-Markdown/markdown/wiki/Tutorial-2---Altering-Markdown-Rendering
    # Why do we use inline styles for HTML emails? Although it doesn't seem
    # necessary for most modern email clients, this is a backward-compatibility
    # strategy.
    # https://www.litmus.com/blog/do-email-marketers-and-designers-still-need-to-inline-css/
    def run(self, root):
        for element in root.iter('h1'):
            element.set('style', 'margin-top: 36px; margin-bottom: 16px; font-size: 22px;color: #162e51;font-family: Merriweather,Merriweather Web,Merriweather Web,Tinos,Georgia,Cambria,Times New Roman,Times,serif;line-height: 1.5;font-weight: 700;')
            div = Element('div')
            div.set('style', 'margin-top: 8px; border: 2px solid #162e51; border-radius: 2px; background: #162e51; width: 25px;')
            element.append(div)
        for element in root.iter('h2'):
            element.set('style', 'margin-top: 36px; margin-bottom: 16px; font-size: 20px;color: #162e51;font-family: Merriweather,Merriweather Web,Merriweather Web,Tinos,Georgia,Cambria,Times New Roman,Times,serif;line-height: 1.5;font-weight: 700;')


class CustomHTMLExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(CustomHTMLProcessor(md), 'custom_html_processor', 15)


def crt_send_mail(report, template, purpose=TMSEmail.MANUAL_EMAIL):
    """
    Given a report and a template, use django's builtin `send_mail` to generate and send
    an outbound email

    Returns a reference to the delivered TMSAPI request
    """
    subject = template.render_subject(report)
    message = template.render_body(report)

    recipient_list = remove_disallowed_recipients([report.contact_email])
    if not recipient_list:
        logger.info(f'{report.contact_email} not in allowed domains, not attempting to deliver email response template #{template.id} to report: {report.id}')
        return None

    if template.is_html:
        md = markdown.markdown(message, extensions=['extra', 'sane_lists', 'admonition', 'nl2br', CustomHTMLExtension()])
        html_message = render_to_string('email.html', {'content': md})
    else:
        # replace newlines, \n, with <br> so the API will generate formatted emails
        html_message = message.replace('\n', '<br>')

    send_results = send_mail(
        subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list,
        fail_silently=False, html_message=html_message
    )
    logger.info(f'Sent email response template #{template.id} to report: {report.id}')
    if settings.EMAIL_BACKEND == 'tms.backend.TMSEmailBackend':
        response = send_results[0]
        TMSEmail(tms_id=response['id'],
                 recipient=report.contact_email,
                 subject=subject,
                 body=message,
                 report=report,
                 created_at=datetime.strptime(response['created_at'], '%Y-%m-%dT%H:%M:%S%z'),
                 status=response['status'],
                 purpose=purpose
                 ).save()
    return send_results


def combine_email_content(report_id, referral):
    report = get_object_or_404(Report, pk=report_id)
    report.contact_address_line_1
    report.contact_address_line_2
    report.contact_city
    report.contact_state
    report.contact_zip
    report.contact_phone
    report.contact_email
    report.violation_summary