from django.core.management.base import BaseCommand
from cts_forms.models import ScheduledNotification
from cts_forms.mail import notify_scheduled


class Command(BaseCommand):
    help = 'Sends any scheduled digest notifications'

    def handle(self, *args, **options):
        for notification in ScheduledNotification.find_ready_to_send():
            try:
                notify_scheduled(notification)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending notification {notification.id}: {e}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Sent notification {notification.id}'))
