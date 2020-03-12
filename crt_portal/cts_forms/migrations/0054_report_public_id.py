# Generated by Django 2.2.10 on 2020-03-09 22:44
import random

from django.db import migrations, models

from cts_forms.signals import salt


def add_old_id(apps, schema_editor):
    # remove other codes from "other" code from "Other", since codes are unique
    Report = apps.get_model('cts_forms', 'Report')
    old_reports = Report.objects.filter(public_id='x')
    for report in old_reports:
        salt_chars = salt()
        report.public_id = f'{report.pk}-{salt_chars}'
        report.save()


class Migration(migrations.Migration):
    dependencies = [
        ('cts_forms', '0053_add_email_as_intake'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='public_id',
            field=models.CharField(default='x', max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(add_old_id)
    ]
