# Generated by Django 4.2.3 on 2023-12-26 20:47

from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission
from django.db import migrations


def _create_permission(apps, schema_editor):
    del schema_editor  # Unused
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def _delete_permission(apps, schema_editor):
    del apps, schema_editor  # Unused
    try:
        Permission.objects.get(codename='approve_disposition').delete()
    except Permission.DoesNotExist:
        pass


def _add_group(apps, schema_editor):
    del apps, schema_editor  # Unused
    group = Group.objects.create(name='Section Disposition Staff')
    group.permissions.add(
        Permission.objects.get(codename='approve_disposition')
    )
    group.save()


def _remove_group(apps, schema_editor):
    del apps, schema_editor  # Unused
    Group.objects.get(name='Section Disposition Staff').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0189_alter_routingsection_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='retentionschedule',
            options={'permissions': (('assign_retentionschedule', 'Can assign retention schedules to reports'), ('approve_disposition', 'Can approve disposition of reports'))},
        ),
        migrations.RunPython(_create_permission, _delete_permission),
        migrations.RunPython(_add_group, _remove_group),
    ]