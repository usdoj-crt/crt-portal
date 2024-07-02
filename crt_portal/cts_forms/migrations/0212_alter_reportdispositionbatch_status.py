# Generated by Django 4.2.11 on 2024-06-21 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0211_alter_reportdispositionbatch_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportdispositionbatch',
            name='status',
            field=models.TextField(choices=[('ready', 'Ready'), ('verified', 'Verified'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('archived', 'Archived')], default='ready'),
        ),
    ]