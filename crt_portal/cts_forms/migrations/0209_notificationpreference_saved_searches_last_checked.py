# Generated by Django 4.2.11 on 2024-05-22 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0208_notificationpreference_saved_searches'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationpreference',
            name='saved_searches_last_checked',
            field=models.JSONField(blank=True, default=dict, help_text='The last time each search was checked for new reports.'),
        ),
    ]