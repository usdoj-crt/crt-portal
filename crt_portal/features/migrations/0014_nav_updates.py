# Generated by Django 4.2.3 on 2024-04-26 11:43

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0013_saved_searches'),
    ]

    operations = [
        AddFeatureMigration(
            'nav-updates',
            False,
            description='Show new main side navigation'
        ),
    ]
