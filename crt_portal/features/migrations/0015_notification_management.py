# Generated by Django 4.2.11 on 2024-05-08 20:27

from django.db import migrations
from features.models import AddFeatureMigration


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0014_nav_updates'),
    ]

    operations = [
        AddFeatureMigration(
            'notification-management',
            True,
            description='Show the notification management page'
        ),
    ]