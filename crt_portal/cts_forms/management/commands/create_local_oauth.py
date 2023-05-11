from django.core.management.base import BaseCommand
from oauth2_provider.models import Application
from oauth2_provider import generators


class Command(BaseCommand):  # pragma: no cover
    help = "Shorthand to up Jupyter as a local oauth client."

    def handle(self, *args, **options):
        # Use oauth2_provider to generate client_id and client_secret
        client_id = generators.generate_client_id()
        client_secret = generators.generate_client_secret()
        Application.objects.all().delete()
        Application.objects.create(
            name='JupyterHub',
            client_id=client_id,
            client_secret=client_secret,
            client_type='confidential',
            authorization_grant_type='authorization-code',
            redirect_uris='http://localhost:8001/hub/oauth_callback',
            algorithm='HS256',
            skip_authorization=True,
        )
        with open('.env', 'a+') as env_file:
            env_file.seek(0)
            lines = [
                line for line in
                env_file.readlines()
                if not line.startswith('OAUTH_PROVIDER_')
            ]
            env_file.seek(0)
            env_file.truncate()
            env_file.writelines([
                *lines,
                f"OAUTH_PROVIDER_CLIENT_ID='{client_id}'\n",
                f"OAUTH_PROVIDER_CLIENT_SECRET='{client_secret}'\n",
            ])
        self.stdout.write(self.style.SUCCESS('Added JupyterHub as a local oauth application, and updated `.env`.'))
        self.stdout.write(self.style.SUCCESS('Please run `docker compose stop jupyter && docker compose up -d jupyter` for changes to take effect.)'))
