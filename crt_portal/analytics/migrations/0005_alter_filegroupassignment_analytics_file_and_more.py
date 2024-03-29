# Generated by Django 4.2.3 on 2023-09-08 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_dashboardgroup_filegroupassignment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filegroupassignment',
            name='analytics_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.analyticsfile'),
        ),
        migrations.AlterField(
            model_name='filegroupassignment',
            name='dashboard_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.dashboardgroup'),
        ),
    ]
