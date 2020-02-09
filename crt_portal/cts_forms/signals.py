""" This enables the logging needed for good forensics and compliance.
inspired by https://www.algotech.solutions/blog/python/using-django-signals-for-database-logging/
"""
import logging

from crequest.middleware import CrequestMiddleware

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import Report, ProtectedClass, InternalHistory

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_user_message(action, current_request, instance):
    # CLI in the case that someone is using the python shell, in that case more log will be available outside the app in cloud.gov
    ip = get_client_ip(current_request) if current_request else 'CLI'
    username = current_request.user.username if current_request else 'CLI'
    userid = current_request.user.id if current_request else 'CLI'
    return f'ADMIN ACTION by: {username} {userid} @ {ip} User {action}: {instance.pk} permissions: {instance.user_permissions.all()} staff: {instance.is_staff} superuser: {instance.is_superuser} active: {instance.is_active}'


def format_data_message(action, current_request, instance):
    # public users will not have usernames, but they will have ip addresses
    ip = get_client_ip(current_request) if current_request else 'CLI'
    username = current_request.user.username if current_request else 'CLI'
    userid = current_request.user.id if current_request else 'CLI'
    details = str(instance.__dict__)
    return f'DATA ACTION by: {username} {userid} @ {ip} {action}: {instance.pk} -- {details}'


@receiver(post_save, sender=User)
def save_user(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    message = format_user_message('saved', current_request, instance)
    logger.info(message)


@receiver(post_delete, sender=User)
def delete_user(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    message = format_user_message('deleted', current_request, instance)
    logger.info(message)


@receiver(user_logged_in)
def user_login(sender, **kwargs):
    current_request = CrequestMiddleware.get_request()
    username = current_request.user.username if current_request else 'CLI'
    userid = current_request.user.id if current_request else 'CLI'
    ip = get_client_ip(current_request) if current_request else 'CLI'
    logger.info(f'User login: {username} {userid} @ {ip}')


@receiver(user_logged_out)
def user_logout(sender, **kwargs):
    current_request = CrequestMiddleware.get_request()
    username = current_request.user.username if current_request else 'CLI'
    userid = current_request.user.id if current_request else 'CLI'
    ip = get_client_ip(current_request) if current_request else 'CLI'
    logger.info(f'User logout: {username} {userid} @ {ip}')


@receiver(pre_save, sender=InternalHistory)
def add_author(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    author = current_request.user.username if current_request else 'anonymous'
    instance.author = author


@receiver(post_save, sender=Report)
@receiver(post_save, sender=ProtectedClass)
@receiver(post_save, sender=InternalHistory)
def save_report(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    message = format_data_message('Data saved', current_request, instance)
    logger.info(message)


@receiver(post_delete, sender=Report)
@receiver(post_delete, sender=ProtectedClass)
@receiver(post_delete, sender=InternalHistory)
def delete_report(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    message = str(format_data_message('DATA DELETED', current_request, instance))
    logger.info(message)
