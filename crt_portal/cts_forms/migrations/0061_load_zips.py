import logging
import os
from csv import DictReader
from pathlib import Path


from django.conf import settings
from django.db import migrations, models

logger = logging.getLogger(__name__)


lockfile = os.path.join(
    settings.BASE_DIR,
    'NO_ZIP.txt'
)
# don't want to load all zip_codes for circle or local testing
if Path(lockfile).is_file():
    load_zips = False
else:
    load_zips = True


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0061_adjust_district_model'),
    ]

    def load_zip_data(apps, schema_editor):
        csv_path = os.path.join(settings.BASE_DIR, '..', 'data/zip_codes_by_district.csv')
        with open(csv_path) as csvfile:
            csvreader = DictReader(csvfile)
            JudicialDistrict = apps.get_model('cts_forms', 'JudicialDistrict')
            # this takes too long and is not needed for tests

            if load_zips is True:
                logger.info('Loading zip codes...')
                for row in csvreader:
                    district = str(row['DISTRICT_NUMBER']) + str(row['DISTRICT_LETTER'])
                    JudicialDistrict.objects.create(
                        zipcode=row['ZIPCODE'],
                        city=row['CITY'],
                        state=row['STATE'],
                        county=row['COUNTY'],
                        district_number=row['DISTRICT_NUMBER'],
                        district_letter=row['DISTRICT_LETTER'],
                        district=district
                    )
            else:
                logger.info('Skipping zip code import')

    operations = [
        migrations.RunPython(load_zip_data),
    ]
