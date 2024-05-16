from typing import Optional

import logging
from actstream import action
from cts_forms.models import Report, ScheduledNotification
from cts_forms.mail import notify, bulk_notify


def send_action(user, *, verb, description, target, send_notification=False, is_bulk=False):
    """Send all actions to activity stream"""
    action.send(
        user,
        verb=verb,
        description=description,
        target=target,
    )
    if send_notification and not is_bulk:
        handle_notify(
            user=user,
            verb=verb,
            description=description,
            target=target,
        )


def _get_frequency(preference_name, *, reports, user, recipient) -> Optional[str]:
    if not reports:
        logging.warning(f'Not notifying {preference_name} (no target report given)')
        return 'none'

    suffix = f'({len(reports)} reports)' if reports else f'(report {reports[0].id})'

    if not recipient:
        logging.info(f'Not notifying {preference_name} (no recipient) {suffix}')
        return 'none'
    if not hasattr(recipient, 'notification_preference'):
        logging.info(f'Not notifying {preference_name} (no notification preference) {suffix}')
        return 'none'

    preference = getattr(recipient.notification_preference, preference_name)
    if preference == 'none':
        logging.info(f'Not notifying {preference_name} (opted out of notification) {suffix}')
        return 'none'
    if not recipient.email:
        logging.warning(f'Not notifying {preference_name} (User {recipient.id} is opted in, but has no email address)')
        return 'none'

    return preference


def _handle_notify(preference_name, *, user, verb, description, target):
    reports = None
    if isinstance(target, Report):
        reports = [target]
    elif target and isinstance(target[0], Report):
        reports = target

    recipient = _get_recipient(preference_name, reports)
    frequency = _get_frequency(preference_name, reports=reports, user=user, recipient=recipient)
    if frequency == 'none':
        return

    if frequency == 'individual':
        _notify_individual(user=user, reports=reports, verb=verb, description=description, target=target, template_title=preference_name, recipient=recipient)
        return

    scheduled = ScheduledNotification.find_for(recipient=recipient, frequency=frequency)
    scheduled.notifications[preference_name].extend([
        {'report': {'id': report.id}}
        for report in reports
    ])
    scheduled.save()


def _notify_individual(user, *, reports, verb, description, target, template_title, recipient):
    if len(reports) == 1:
        notify(template_title=template_title,
               report=reports[0],
               recipients=[recipient.email],
               actstream={
                   'user': user,
                   'verb': verb,
                   'description': description,
                   'target': target,
               })
        return

    bulk_notify(template_title=f'{template_title}_bulk',
                report=reports[0],
                reports=reports,
                recipients=[recipient.email],
                actstream={
                    'user': user,
                    'verb': verb,
                    'description': description,
                    'targets': target})


def _get_recipient(preference_name, reports):
    if preference_name == 'assigned_to' and reports:
        return reports[0].assigned_to
    return None


def handle_notify(*, user, verb, description, target):
    kwargs = {
        'user': user,
        'verb': verb,
        'description': description,
        'target': target,
    }
    verb = kwargs.get('verb', None)
    if verb == 'Assigned to:':
        return _handle_notify('assigned_to', **kwargs)
