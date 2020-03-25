from csv import DictReader
from django.db import migrations
from .models import JudicialDistrict


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0060_add_judicial_class'),
    ]

    def load_zip_data(*args, **defaults):
        with open('data/zip_codes_by_district.csv', newline='') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=' ', quotechar='|')
            for row in csvreader:
                JudicialDistrict.create(
                    zipcode=row['ZIPCODE'],
                    city=row['CITY'],
                    state=row['STATE'],
                    county=row['COUNTY'],
                )

    operations = [
        migrations.RunPython(load_zip_data),
    ]
