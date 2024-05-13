from typing import Optional

import logging
from actstream import action
from cts_forms.models import Report
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


def _get_assigned_to_frequency(*, reports, user) -> Optional[str]:
    if not reports:
        logging.warning('Not notifying assignee (no target report given)')
        return 'none'

    suffix = f'({len(reports)} reports)' if reports else f'(report {reports[0].id})'

    if not reports[0].assigned_to:
        logging.info(f'Not notifying assignee (no assignee) {suffix}')
        return 'none'
    if not hasattr(reports[0].assigned_to, 'notification_preference'):
        logging.info(f'Not notifying assignee (no notification preference) {suffix}')
        return 'none'

    preference = reports[0].assigned_to.notification_preference.assigned_to == 'none'
    if preference == 'none':
        logging.info(f'Not notifying assignee (opted out of notification) {suffix}')
        return 'none'
    if not reports[0].assigned_to.email:
        logging.warning(f'Not notifying assignee (User {reports[0].assigned_to.id} is opted in, but has no email address)')
        return 'none'

    return preference


def _handle_notify_assigned_to(*, user, verb, description, target):
    reports = None
    if isinstance(target, Report):
        reports = [target]
    elif target and isinstance(target[0], Report):
        reports = target

    frequency = _get_assigned_to_frequency(reports=reports, user=user)
    if frequency == 'none':
        return

    if frequency == 'individual':
        _notify_individual(user=user, reports=reports, verb=verb, description=description, target=target)
        return

    raise NotImplementedError(f'Unsupported frequency: {frequency}')


def _notify_individual(user, *, reports, verb, description, target):
    if len(reports) == 1:
        notify(template_title='assigned_to',
               report=reports[0],
               recipients=[reports[0].assigned_to.email],
               actstream={
                   'user': user,
                   'verb': verb,
                   'description': description,
                   'target': target,
               })
        return

    bulk_notify(template_title='assigned_to_bulk',
                report=reports[0],
                reports=reports,
                recipients=[reports[0].assigned_to.email],
                actstream={
                    'user': user,
                    'verb': verb,
                    'description': description,
                    'targets': target,
                })


def handle_notify(*, user, verb, description, target):
    kwargs = {
        'user': user,
        'verb': verb,
        'description': description,
        'target': target,
    }
    verb = kwargs.get('verb', None)
    if verb == 'Assigned to:':
        return _handle_notify_assigned_to(**kwargs)
