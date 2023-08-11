import types
from typing import List, Optional
import logging
from django.forms.models import model_to_dict
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
# bandit flags ANY import from ElementTree, not just parse-related ones.
# Element is not a parser and there is no alternative to importing from `xml`.
from xml.etree.ElementTree import Element  # nosec
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from cts_forms.models import Report
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


class Mail(types.SimpleNamespace):
    recipients: Optional[List[str]]
    subject: Optional[str]
    message: Optional[str]
    html_message: Optional[str]


def render_agency_mail(*, complainant_letter: Mail, report, template, extra_ccs=None) -> Optional[Mail]:
    if not template.referral_contact:
        return None
    if not extra_ccs:
        extra_ccs = []
    message = _build_referral_content(complainant_letter=complainant_letter, template=template, report=report)

    recipients = template.referral_contact.clean_addressee_emails()
    all_recipients = (recipients + extra_ccs) if recipients else []
    allowed_recipients = remove_disallowed_recipients(all_recipients)

    return Mail(message=message,
                html_message=message,
                recipients=allowed_recipients,
                subject=f'[DOJ CRT Referral] {report.public_id} - {report.contact_full_name}',
                )


def render_complainant_mail(*, report, template) -> Mail:
    message = template.render_body(report)

    if template.is_html:
        md = markdown.markdown(message, extensions=['extra', 'sane_lists', 'admonition', 'nl2br', CustomHTMLExtension()])
        html_message = render_to_string('email.html', {'content': md})
    else:
        # replace newlines, \n, with <br> so the API will generate formatted emails
        html_message = message.replace('\n', '<br>')

    if not report.contact_email:
        recipients = []
    else:
        recipients = remove_disallowed_recipients([report.contact_email])

    return Mail(
        subject=template.render_subject(report),
        message=template.render_body(report),
        html_message=html_message,
        recipients=recipients,
    )


def send_tms(message: Mail, *, report: Report, purpose: str, dry_run: bool) -> List[int]:
    if settings.EMAIL_BACKEND != 'tms.backend.TMSEmailBackend':
        TMSEmail.create_fake(subject=message.subject,
                             body=message.message,
                             html_body=message.html_message,
                             report=report,
                             purpose=purpose
                             ).save()
        return [1]

    if dry_run:
        return [0]

    if not message.subject or not message.message or not message.recipients:
        return [0]

    send_results = send_mail(
        message.subject,
        message.message,
        settings.DEFAULT_FROM_EMAIL,
        message.recipients,
        fail_silently=False,
        html_message=message.html_message
    )
    response = send_results[0]
    TMSEmail(tms_id=response['id'],
             recipient=message.recipients,
             subject=message.subject,
             body=message.message,
             html_body=message.html_message,
             report=report,
             created_at=datetime.strptime(response['created_at'], '%Y-%m-%dT%H:%M:%S%z'),
             status=response['status'],
             purpose=purpose
             ).save()

    return send_results


def mail_to_complainant(report, template, purpose=TMSEmail.MANUAL_EMAIL, dry_run=False, rendered=None):
    """
    Given a report and a template, use django's builtin `send_mail` to generate and send
    an outbound email

    Returns a list of integers indicating the number of successfully sent emails.
    """
    if not rendered:
        rendered = render_complainant_mail(report=report, template=template)
    if not rendered.recipients:
        logger.info(f'{report.contact_email} not in allowed domains, not attempting to deliver email response template #{template.id} to report: {report.id}')
        return None

    send_results = send_tms(rendered, report=report, purpose=purpose, dry_run=dry_run)
    logger.info(f'Sent email response template #{template.id} to report: {report.id}')

    return send_results


def _build_referral_content(*, complainant_letter, template, report) -> Optional[str]:
    if not template.referral_contact:
        return None
    data = {
        'complainant_letter': complainant_letter,
        'template': model_to_dict(template),
        'referral_contact': model_to_dict(template.referral_contact),
        'report': model_to_dict(report),
    }
    return render_to_string('referral_info.html', data)
