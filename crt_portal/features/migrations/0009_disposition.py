# Generated by Django 4.2.3 on 2023-09-06 14:23

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0008_data_dashboard'),
    ]

    operations = [
        AddFeatureMigration(
            'disposition',
            False,
            description='Show disposition features (report form inputs, filters, etc)'
        ),
    ]
