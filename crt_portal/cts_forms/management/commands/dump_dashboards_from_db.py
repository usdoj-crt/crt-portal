import json
import os

from analytics.models import get_dashboard_structure_from_db

from django.conf import settings
from django.core.management.base import BaseCommand

NOTEBOOK_DIR = os.path.join(settings.BASE_DIR, '..', 'jupyterhub')


class Command(BaseCommand):  # pragma: no cover
    help = 'Save the database dashboard state so it can be reloaded.'

    def handle(self, *args, **options):
        del args, options  # Unused

        structure = get_dashboard_structure_from_db(include_content=False)
        with open(os.path.join(NOTEBOOK_DIR, 'dashboards.json'), 'w') as f:
            json.dump(structure, f, indent=2, sort_keys=True)

        self.stdout.write(self.style.SUCCESS('Wrote ./jupyterhub/dashboards.json'))
