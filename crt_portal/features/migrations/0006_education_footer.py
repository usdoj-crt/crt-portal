# Generated by Django 3.2.17 on 2023-06-27 20:55

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0005_edit_outreach'),
    ]

    operations = [
        AddFeatureMigration('education-footer', False,
                            description='Hides/shows the Learn More link and Notes section of the education cards on the homepage.'),
    ]
