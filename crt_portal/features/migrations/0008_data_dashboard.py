# Generated by Django 4.2.3 on 2023-09-06 14:23

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0007_separate_referrals_workflow'),
    ]

    operations = [
        AddFeatureMigration(
            'data-dashboard',
            False,
            description='Show the Data Dashboard (Jupyter) reporting tab next to "Team Management" and "Report Records"'
        ),
    ]
