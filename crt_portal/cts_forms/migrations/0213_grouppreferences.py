# Generated by Django 4.2.3 on 2024-06-26 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('cts_forms', '0212_alter_reportdispositionbatch_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_searches', models.JSONField(blank=True, default=dict, help_text='Contains the notification cadence for each saved search. The key is the saved search ID, and the value is the cadence.')),
                ('admins', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='group_preferences', to='auth.group')),
            ],
        ),
    ]