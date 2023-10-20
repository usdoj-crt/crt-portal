import secrets

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):  # pragma: no cover
    help = "Creates a mock user for testing."

    def handle(self, *args, **options):
        password = secrets.token_hex(32)
        userhash = secrets.token_hex(32)
        username = f'test-user-{userhash}'

        # Clean out any existing test users to avoid conflicts:
        User.objects.filter(username__startswith='test-user-').delete()

        User.objects.create_superuser(
            username=username,
            email=f'{username}@example.com',
            password=password
        )

        # Write the password to the current directory, so CI/CD can read it:
        with open('test-user-username.txt', 'w') as f:
            f.write(username)
        with open('test-user-password.txt', 'w') as f:
            f.write(password)
