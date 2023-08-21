from django.core.management.base import BaseCommand
from oauth2_provider.models import Application
from oauth2_provider import generators


class Command(BaseCommand):  # pragma: no cover
    help = "Shorthand to up Jupyter as an oauth client."

    def add_arguments(self, parser):
        parser.add_argument(
            '--write-to-env',
            action='store_true',
            help='Write the client_id and client_secret to .env instead of stdout',
        )

        parser.add_argument(
            '--cf-set-env',
            action='store_true',
            help='Output a cf set-env command (as a string)',
        )

        parser.add_argument(
            '--redirect_uris',
            type=str,
            default='',
            help='Space-separated redirect_uris to use. If this is present, --port is ignored',
        )

        parser.add_argument(
            '--port',
            type=int,
            default=8001,
            help='The port that JupyterHub is running on',
        )

    def handle(self, *args, **options):
        # Use oauth2_provider to generate client_id and client_secret
        client_id = generators.generate_client_id()
        client_secret = generators.generate_client_secret()
        jupyter_port = options.get('port')
        manual_redirect_uris = options.get('redirect_uris')
        redirect_uris = manual_redirect_uris or f'http://localhost:{jupyter_port}/hub/oauth_callback'

        Application.objects.all().delete()
        Application.objects.create(
            name='JupyterHub',
            client_id=client_id,
            client_secret=client_secret,
            client_type='confidential',
            authorization_grant_type='authorization-code',
            redirect_uris=redirect_uris,
            algorithm='HS256',
            skip_authorization=True,
        )

        if options.get('cf_set_env'):
            preamble = 'cf set-env crt-portal-jupyter'
            print(f'{preamble} OAUTH_PROVIDER_CLIENT_ID {client_id} && '
                  f'{preamble} OAUTH_PROVIDER_CLIENT_SECRET {client_secret}')
            return

        if not options.get('write_to_env'):
            print(f'OAUTH_PROVIDER_CLIENT_ID={client_id}')
            print(f'OAUTH_PROVIDER_CLIENT_SECRET={client_secret}')
            return

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
