# Generated by Django 2.2.24 on 2022-01-06 16:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0135_materialize_email_count_view'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='crt_reciept_year',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name=django.core.validators.MaxValueValidator(2022)),
        ),
        migrations.AlterField(
            model_name='report',
            name='last_incident_year',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name=django.core.validators.MaxValueValidator(2022, message='Date can not be in the future.')),
        ),
    ]
