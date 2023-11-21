import logging
from actstream import action
from cts_forms.models import Report
from cts_forms.mail import notify
from django.contrib import messages


def send_action(user, *, verb, description, target, send_notification=False):
    """Send all actions to activity stream"""
    action.send(
        user,
        verb=verb,
        description=description,
        target=target,
    )
    if send_notification:
        _handle_notify(
            user=user,
            verb=verb,
            description=description,
            target=target,
        )


def _handle_notify_assigned_to(*, user, verb, description, target):
    report = target if isinstance(target, Report) else None
    if not report:
        logging.warning('Not notifying assignee (no target report given)')
        return
    if not report.assigned_to:
        logging.info(f'Not notifying assignee (no assignee) (report {report.id})')
        return
    if not hasattr(report.assigned_to, 'notification_preference'):
        messages.add_message()
        logging.info(f'Not notifying assignee (no notification preference) (report {report.id})')
        return
    if not report.assigned_to.notification_preference.assigned_to:
        messages.add_message()
        logging.info(f'Not notifying assignee (opted out of notification) (report {report.id})')
        return
    if not report.assigned_to.email:
        messages.add_message()
        logging.warning(f'Not notifying assignee (User {report.assigned_to.id} is opted in, but has no email address)')
        return
    notify(template_title='assigned_to',
           report=report,
           recipients=[report.assigned_to.email],
           actstream={
               'user': user,
               'verb': verb,
               'description': description,
               'target': target,
           })


def _handle_notify(*, user, verb, description, target):
    kwargs = {
        'user': user,
        'verb': verb,
        'description': description,
        'target': target,
    }
    verb = kwargs.get('verb', None)
    if verb == 'Assigned to:':
        return _handle_notify_assigned_to(**kwargs)
