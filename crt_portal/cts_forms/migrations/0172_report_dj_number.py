# Generated by Django 3.2.17 on 2023-04-13 13:19

import cts_forms.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0171_campaign_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='dj_number',
            field=models.CharField(blank=True, max_length=256, null=True, validators=[cts_forms.validators.validate_dj_number]),
        ),
    ]
