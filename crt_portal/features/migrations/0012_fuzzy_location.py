# Generated by Django 4.2.3 on 2023-12-15 18:04

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0011_tags'),
    ]

    operations = [
        AddFeatureMigration(
            'fuzzy-location-name',
            False,
            description='Show tags throughout the application'
        ),
    ]