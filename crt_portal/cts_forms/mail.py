import types
from typing import List, Optional, Tuple
import logging
from django.forms.models import model_to_dict
import markdown

from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from cts_forms.models import Report, ResponseTemplate, ScheduledNotification, SavedSearch
from tms.models import TMSEmail
from utils.markdown_extensions import RelativeToAbsoluteLinkExtension, CustomHTMLExtension
from utils.site_prefix import get_site_prefix

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


class Mail(types.SimpleNamespace):
    recipients: Optional[List[str]]
    disallowed_recipients: Optional[List[str]]
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
    disallowed_recipients = list(set(all_recipients) - set(allowed_recipients))

    return Mail(message=message,
                html_message=message,
                recipients=allowed_recipients,
                disallowed_recipients=disallowed_recipients,
                subject=f'[DOJ CRT Referral] {report.public_id} - {report.contact_full_name}',
                )


def render_complainant_mail(*, report, template, action) -> Mail:
    templates_to_add_emails_to = [
        "DRS - Notice of Right to Sue",
        "DRS - Notice of Right to Sue (Conciliation Failure)",
        "ELS - Notice of Right to Sue",
        "ELS - Notice of Right to Sue (Conciliation Failure) form letter",
    ]
    all_recipients = report.contact_emails
    allowed_recipients = remove_disallowed_recipients(all_recipients)
    disallowed_recipients = list(set(all_recipients) - set(allowed_recipients))

    if template.title in templates_to_add_emails_to:
        template.body = f"{template.body.rstrip()}\n\nCC: {', '.join(allowed_recipients)}"

    content = template.render_body_as_markdown(report, extensions=[CustomHTMLExtension()])

    html_source = 'print.html' if action == 'print' else 'email.html'
    html_message = render_to_string(html_source,
                                    {'content': content, 'report': report})

    return Mail(
        subject=template.render_subject(report),
        message=template.render_plaintext(report),
        html_message=html_message,
        recipients=allowed_recipients,
        disallowed_recipients=disallowed_recipients,
    )


def _render_notification_mail(*,
                              report: Optional[Report],
                              template: ResponseTemplate,
                              recipients: List[str],
                              reports: Optional[List[Report]] = None,
                              **kwargs) -> Mail:

    if reports:
        message = template.render_bulk_body(report, reports, **kwargs)
        subject = template.render_bulk_subject(report, reports, **kwargs)
    else:
        message = template.render_body(report, **kwargs)
        subject = template.render_subject(report, **kwargs)

    md = markdown.markdown(message, extensions=['extra', 'sane_lists', 'admonition', 'nl2br', CustomHTMLExtension(), RelativeToAbsoluteLinkExtension(for_intake=True)])
    html_message = render_to_string('notification.html', {
        'content': md,
        'unsubscribe_link': '/'.join([get_site_prefix(for_intake=True), 'form/notifications']),
    })

    allowed_recipients = remove_disallowed_recipients(recipients)
    disallowed_recipients = list(set(recipients) - set(allowed_recipients))

    return Mail(message=message,
                html_message=html_message,
                recipients=allowed_recipients,
                disallowed_recipients=disallowed_recipients,
                subject=f'[CRT Portal] {subject}')


def _render_digest(notification):
    report_id = notification['report']['id']
    return f'[Report {report_id}](/form/view/{report_id})'


def _render_digests(kind, scheduled: ScheduledNotification):
    extensions = ['extra', 'sane_lists', 'admonition', 'nl2br', CustomHTMLExtension(), RelativeToAbsoluteLinkExtension(for_intake=True)]
    if kind == 'assigned_to':
        items = list(set([
            markdown.markdown(_render_digest(notification), extensions=extensions)
            for notification in scheduled.notifications[kind]
        ]))
    else:
        items = None

    if kind == 'assigned_to':
        title = 'You have been assigned to the following reports:'
    elif kind.startswith('saved_search_'):
        search_name = scheduled.notifications[kind]['name']
        new_reports = scheduled.notifications[kind]['new_reports']
        search_id = kind.split('_')[-1]
        try:
            search = SavedSearch.objects.get(pk=int(search_id))
        except SavedSearch.DoesNotExist:
            return None
        start_date = scheduled.created_at.isoformat().split('T')[0]
        url = f'{search.get_absolute_url()}&create_date_start={start_date}'
        title = f'There are {new_reports} new reports matching your search "[{search_name}]({url})"'

    return {
        'title': markdown.markdown(title, extensions=extensions),
        'items': items
    }


def _render_scheduled_notification_mail(scheduled: ScheduledNotification) -> Mail:
    saved_search_groups = [key for key
                           in scheduled.notifications
                           if key.startswith('saved_search_')]

    digests = [
        _render_digests(kind, scheduled)
        for kind in ['assigned_to', *saved_search_groups]
        if kind in scheduled.notifications
    ]

    digests = [digest for digest in digests if digest]

    html_message = render_to_string('scheduled_notification.html', {
        'digests': digests,
        'unsubscribe_link': '/'.join([get_site_prefix(for_intake=True), 'form/notifications']),
    })

    recipients = [scheduled.recipient.email]

    allowed_recipients = remove_disallowed_recipients(recipients)
    disallowed_recipients = list(set(recipients) - set(allowed_recipients))

    return Mail(message=html_message,
                html_message=html_message,
                recipients=allowed_recipients,
                disallowed_recipients=disallowed_recipients,
                subject=f'[CRT Portal] {scheduled.frequency} notification digest')


def send_tms(message: Mail, *, report: Optional[Report], purpose: str, dry_run: bool) -> List[int]:
    if dry_run:
        return [0]

    if not message.subject or not message.message:
        return [0]

    if message.recipients:
        send_results = send_mail(
            message.subject,
            message.message,
            settings.DEFAULT_FROM_EMAIL,
            message.recipients,
            fail_silently=False,
            html_message=message.html_message
        )
        response = send_results if isinstance(send_results, int) else send_results[0]
    else:
        # This should only happen on non-production sites, so use a fake TMS response:
        send_results = [0]
        response = {'id': 0, 'status': 'failed', 'created_at': datetime.now().isoformat()}
    if not message.recipients or settings.EMAIL_BACKEND != 'tms.backend.TMSEmailBackend':
        TMSEmail.create_fake(subject=message.subject,
                             body=message.message,
                             html_body=message.html_message,
                             report=report,
                             recipient=message.recipients + message.disallowed_recipients,
                             purpose=purpose
                             ).save()
    else:
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


def notify_scheduled(scheduled: ScheduledNotification):
    """Sends a set of scheduled notifications as a digest."""
    scheduled.was_sent = True
    scheduled.save()

    if not scheduled.recipient.email:
        logger.info(f'Not sending digest notification (no email address for {scheduled.recipient})')
        return

    message = _render_scheduled_notification_mail(scheduled)

    logger.info(f'Digest Notification sent to {message.recipients}')

    send_tms(message,
             report=None,
             purpose=TMSEmail.NOTIFICATION,
             dry_run=False)


def notify(template_title: str,
           *,
           report: Optional[Report],
           recipients: List[str],
           **kwargs):
    """Sends a notification to an internal user, if they have the preference enabled."""
    try:
        template = ResponseTemplate.objects.get(title=template_title)
    except ResponseTemplate.DoesNotExist as e:
        raise ValueError(f'Cannot send notification (no template with title {template_title})') from e
    message = _render_notification_mail(report=report,
                                        template=template,
                                        recipients=recipients,
                                        reports=None,
                                        **kwargs)

    suffix = f' about report {report.id}' if report else ''
    logger.info(f'Notification ({template.title}) sent to {message.recipients}{suffix}')

    send_tms(message,
             report=report,
             purpose=TMSEmail.NOTIFICATION,
             dry_run=False)


def bulk_notify(template_title: str,
                *,
                report: Optional[Report],
                reports: List[Report],
                recipients: List[str],
                **kwargs):
    """Sends a notification to an internal user, if they have the preference enabled."""
    try:
        template = ResponseTemplate.objects.get(title=template_title)
    except ResponseTemplate.DoesNotExist as e:
        raise ValueError(f'Cannot send notification (no template with title {template_title})') from e
    message = _render_notification_mail(report=report,
                                        template=template,
                                        recipients=recipients,
                                        reports=reports,
                                        **kwargs)

    suffix = f' about {len(reports)} reports'
    logger.info(f'Notification ({template.title}) sent to {message.recipients}{suffix}')

    send_tms(message,
             report=reports[0],
             purpose=TMSEmail.NOTIFICATION,
             dry_run=False)


def mail_to_complainant(report, template, purpose=TMSEmail.MANUAL_EMAIL, dry_run=False, rendered=None):
    """
    Given a report and a template, use django's builtin `send_mail` to generate and send
    an outbound email

    Returns a list of integers indicating the number of successfully sent emails.
    """
    if not rendered:
        rendered = render_complainant_mail(report=report, template=template, action='email')
    if rendered.disallowed_recipients:
        logger.info(f'Some recipients were not in allowed domains for #{template.id} for report: {report.id}')

    send_results = send_tms(rendered, report=report, purpose=purpose, dry_run=dry_run)
    logger.info(f'Sent email response template #{template.id} to report: {report.id}')

    return send_results


def mail_to_agency(report, template, purpose=TMSEmail.MANUAL_EMAIL, *, rendered, dry_run=False):
    """
    Given a report and a template, use django's builtin `send_mail` to generate and send
    an outbound email

    Returns a list of integers indicating the number of successfully sent emails.
    """
    if not rendered.recipients:
        logger.info(f'Attempted to mail response template #{template.id} to an agency, but has no recipients.')
        return None

    send_results = send_tms(rendered, report=report, purpose=purpose, dry_run=dry_run)
    logger.info(f'Sent email response template #{template.id} to report: {report.id} as referral')

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


def build_preview(template, complainant_letter, referral_letter):
    """Turns Mails into a jsonable bunch of metadata for sending replies."""
    complainant = {
        'letter': {
            'recipients': complainant_letter.recipients,
            'subject': complainant_letter.subject,
            'html_message': complainant_letter.html_message,
            'disallowed_recipients': complainant_letter.disallowed_recipients or [],
        }
    }

    if not referral_letter:
        return {'complainant': complainant}

    agency = {
        'letter': {
            'recipients': referral_letter.recipients,
            'subject': referral_letter.subject,
            'html_message': referral_letter.html_message,
            'disallowed_recipients': referral_letter.disallowed_recipients or [],
        },
        'template': model_to_dict(template),
        'referral_contact': model_to_dict(template.referral_contact),
    }
    return {'complainant': complainant, 'agency': agency}


def build_letters(report: Report, template: ResponseTemplate, *, action) -> Tuple[Mail, Optional[Mail]]:
    """Creates Mails related to replying to or referring a template."""
    complainant_letter = render_complainant_mail(report=report,
                                                 template=template,
                                                 action=action)

    if not template.referral_contact:
        return complainant_letter, None

    agency_letter = render_agency_mail(complainant_letter=complainant_letter,
                                       report=report,
                                       template=template,
                                       extra_ccs=[])
    return complainant_letter, agency_letter
