# Generated by Django 3.2.17 on 2023-06-22 13:36

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0004_team_management_redo'),
    ]

    operations = [
        AddFeatureMigration('edit-outreach', True),
    ]
