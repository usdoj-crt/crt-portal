import boto3
from botocore import UNSIGNED
from botocore.client import Config
import logging
import os
from csv import DictReader
from pathlib import Path

from django.conf import settings
from django.db import migrations, models

logger = logging.getLogger(__name__)

# This file is generated if you run test_settings.py
lockfile = os.path.join(
    settings.BASE_DIR,
    'NO_ZIP.txt'
)

# don't want to load all zip_codes for circle or local testing
if Path(lockfile).is_file():
    load_zips = False
else:
    load_zips = True


def fetch_file():  # pragma: no cover
    # no credentials needed to pull from the public bucket
    s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED), region_name='us-gov-west-1')
    # this is a public link in the dev s3 bucket
    bucket = s3.Bucket(u'cg-b2626a97-5c90-4d35-a39b-24f3b035d5c9')
    obj = bucket.Object(key=u'data/zip_codes_by_district.csv')
    return obj.get()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0061_adjust_district_model'),
    ]

    def load_zip_data(apps, schema_editor):  # pragma: no cover
        """This loads all the zip code mappings into the database. It also takes over a minute and is not needed for tests"""
        if load_zips is True:
            JudicialDistrict = apps.get_model('cts_forms', 'JudicialDistrict')
            response = fetch_file()
            lines = response['Body'].read().decode('ascii').split("\n")
            for row in DictReader(lines, delimiter=','):
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

    operations = [
        migrations.RunPython(load_zip_data),
    ]
