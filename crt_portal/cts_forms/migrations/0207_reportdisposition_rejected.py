# Generated by Django 4.2.3 on 2024-05-15 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0206_alter_notificationpreference_assigned_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdisposition',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
    ]