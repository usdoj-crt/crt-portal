# Generated by Django 3.2.17 on 2023-03-03 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShortenedURL',
            fields=[
                ('shortname', models.CharField(help_text='The url the user will type in. For example, putting campaign-1 here would make the URL civilrights.justice.gov/link/campaign-1). Use only letters, numbers, or dashes here.', max_length=255, primary_key=True, serialize=False, unique=True)),
                ('destination', models.TextField(help_text='The destination path, for example /form/view, or /report?utm_campaign=asdf')),
                ('enabled', models.BooleanField(default=True, help_text='If not enabled, the link will result in a 404 - Not Found')),
            ],
        ),
    ]
