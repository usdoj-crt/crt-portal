import logging
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


def build_referral_content(complainant_letter_body, referral_letter_body, report):
    data = {
        'referral_letter': referral_letter_body,
        'complainant_letter': complainant_letter_body,
        'contact_address_line_1': report.contact_address_line_1,
        'contact_address_line_2': report.contact_address_line_2,
        'contact_city': report.contact_city,
        'contact_state': report.contact_state,
        'contact_zip': report.contact_zip,
        'contact_phone': report.contact_phone,
        'contact_email': report.contact_email,
        'primary_complaint': report.primary_complaint,
        'hate_crime': report.hate_crime,
        'commercial_or_public_place': report.commercial_or_public_place,
        'location_name': report.location_name,
        'location_address_line_1': report.location_address_line_1,
        'location_address_line_2': report.location_address_line_2,
        'location_city_town': report.location_city_town,
        'location_state': report.location_state,
        'protected_class': report.protected_class,
        'servicemember': report.servicemember,
        'last_incident_month': report.last_incident_month,
        'last_incident_day': report.last_incident_day,
        'last_incident_year': report.last_incident_year,
        'crt_reciept_year': report.crt_reciept_year,
        'crt_reciept_day': report.crt_reciept_day,
        'crt_reciept_month': report.crt_reciept_month,
        'violation_summary': report.violation_summary,
        'language': report.language,
        'election_details': report.election_details,
        'other_commercial_or_public_place': report.other_commercial_or_public_place,
        'inside_correctional_facility': report.inside_correctional_facility,
        'correctional_facility_type': report.correctional_facility_type,
        'public_or_private_school': report.public_or_private_school,
        'public_or_private_employer': report.public_or_private_employer,
        'employer_size': report.employer_size,
    }
    referral_content_string = render_to_string('referral_info.html', {'data': data})
    return referral_content_string