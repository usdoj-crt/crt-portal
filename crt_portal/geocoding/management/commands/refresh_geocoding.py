import csv
import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from geocoding import models
from django.db import transaction


class Command(BaseCommand):  # pragma: no cover
    help = "Load and migrate section tags"

    load_from_dir = os.path.join(settings.BASE_DIR, 'geocoding')

    def handle(self, *args, **options):
        del args, options  # unused
        for model in models.LOADABLE:
            logging.info(f"Loading {model.LOAD_FROM}")
            self.load_model(model)

    def load_model(self, model):
        model_contents = os.path.join(self.load_from_dir, model.LOAD_FROM)
        with open(model_contents, 'r') as file:
            reader = csv.reader(file)
            headers = [header.lower() for header in next(reader)]
            to_add = [row for row in reader]
        with transaction.atomic():
            model.objects.all().delete()
            model.objects.bulk_create([
                model(**dict(zip(headers, row)))
                for row in to_add
            ])
        logging.info(f'Loaded {len(to_add)} entries for {model.__name__}')
