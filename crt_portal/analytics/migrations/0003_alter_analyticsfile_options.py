# Generated by Django 4.2.3 on 2023-08-25 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_dev_access'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analyticsfile',
            options={'managed': True, 'permissions': (('jupyter_editor', 'Can access and edit Jupyter Notebooks'), ('jupyter_superuser', 'Can use Jupyter admin features'))},
        ),
    ]