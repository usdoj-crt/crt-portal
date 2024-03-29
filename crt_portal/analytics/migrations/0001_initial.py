# Generated by Django 3.2.17 on 2023-05-13 20:57

from django.db import migrations, models
from django.db.migrations.operations import special


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # This table may or may not exist for test instances depending on when
        # the migrations are run. This safely creates or adopts the table:
        migrations.RunSQL(
            "CREATE SCHEMA IF NOT EXISTS analytics",
            reverse_sql=special.RunSQL.noop),
        migrations.RunSQL(
            "CREATE TABLE IF NOT EXISTS analytics.analyticsfile ();",
            reverse_sql="DROP TABLE analytics.analyticsfile"),
        migrations.CreateModel(
            name='AnalyticsFile',
            fields=[],
            options={
                'managed': False,
                'db_table': 'analytics"."analyticsfile',
            },
        ),
        migrations.AlterModelOptions(
            name='AnalyticsFile',
            options={
                'managed': True,
                'db_table': 'analytics"."analyticsfile',
            },
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='name',
            field=models.CharField(help_text='A human-readable name for the notebook', max_length=1024, blank=True, null=False)
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='content',
            field=models.TextField(blank=True, null=True, help_text='The file contents (not human readable, do not edit)')
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='path',
            field=models.CharField(max_length=2048, blank=True, unique=True, null=False, help_text="The full path (including filename) to the file")
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='type',
            field=models.CharField(choices=[('notebook', 'notebook'), ('file', 'file'), ('directory', 'directory')], max_length=32)
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='format',
            field=models.CharField(max_length=1024, blank=True)
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='mimetype',
            field=models.CharField(max_length=1024, blank=True, null=True)
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='created',
            field=models.DateTimeField(blank=True, help_text='When this was created', null=True)
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='last_modified',
            field=models.DateTimeField(blank=True, help_text='When this was last modified', null=True)
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='from_command',
            field=models.BooleanField(default=False, help_text='If true, the notebook was loaded from a command, and should not be modified (e.g., examples)')
        ),
        migrations.AddField(
            model_name='AnalyticsFile',
            name='last_run',
            field=models.DateTimeField(blank=True, help_text='The last time this notebook was run from the Portal admin panel', null=True)
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('analytics.analyticsfile',),
        ),
    ]
