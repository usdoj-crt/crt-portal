# Generated by Django 4.2.20 on 2025-04-21 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0231_shutdownmode'),
    ]

    operations = [
        migrations.AddField(
            model_name='routingsection',
            name='access_section_pocs',
            field=models.CharField(default='', max_length=700, verbose_name='Access Section POCs'),
        ),
    ]
