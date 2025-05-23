# Generated by Django 4.2.11 on 2024-11-08 15:34

from django.db import migrations, models
import django.db.models.deletion
import datetime


def _create_metadata(apps, schema_editor):
    AnalyticsFile = apps.get_model('analytics', 'AnalyticsFile')
    AnalyticsFileMetadata = apps.get_model('analytics', 'AnalyticsFileMetadata')

    metadata = []
    for analytics_file in AnalyticsFile.objects.filter(type='notebook').exclude(path__endswith='/.ipynb_checkpoints'):
        is_dashboard = 'assignments/intake-dashboard' in analytics_file.path
        hourly = datetime.timedelta(hours=1)

        metadata.append(AnalyticsFileMetadata(
            analytics_file=analytics_file,
            run_frequency=hourly if is_dashboard else None,
            discoverable=is_dashboard,
            url=analytics_file.path.replace('.ipynb', '').replace('assignments/intake-dashboard/', ''),
            last_run=None,
        ))
    AnalyticsFileMetadata.objects.bulk_create(metadata)


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0009_alter_analyticsfile_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analyticsfile',
            name='last_run',
        ),
        migrations.CreateModel(
            name='AnalyticsFileMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_frequency', models.DurationField(blank=True, help_text="How often to run this notebook - for example, '1 hour' or '5 days'", null=True)),
                ('discoverable', models.BooleanField(default=False, help_text="Whether this notebook should be displayed in the Portal's intake section")),
                ('url', models.CharField(help_text='The URL to the notebook from the portal (under /form/data/<the_url>', max_length=2048, null=True, unique=True)),
                ('last_run', models.DateTimeField(blank=True, help_text='The last time this notebook was run from the Portal admin panel', null=True)),
                ('analytics_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='analytics.analyticsfile')),
            ],
            options={
                'db_table': 'analytics"."analyticsfilemetadata',
                'managed': True,
            },
        ),
        migrations.RunPython(_create_metadata, migrations.RunPython.noop),
    ]
