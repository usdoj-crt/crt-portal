# Generated by Django 4.2.3 on 2024-08-01 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0214_report_contact_inmate_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportattachment',
            name='report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attachments', to='cts_forms.report'),
        ),
    ]