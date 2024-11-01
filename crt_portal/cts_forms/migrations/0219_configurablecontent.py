# Generated by Django 4.2.11 on 2024-10-03 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0218_resource_background_resource_need_followup_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigurableContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.CharField(help_text='A short, non-changing name to be used in template code.', max_length=500, unique=True)),
                ('content', models.TextField(blank=True, help_text='The content to display in the template.')),
            ],
        ),
    ]