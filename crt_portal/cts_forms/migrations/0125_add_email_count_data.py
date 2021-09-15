import logging

from django.db import migrations, models


logger = logging.getLogger(__name__)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0124_null_in_email_count'),
    ]

    def backfill_email_count(apps, schema_editor):
        Report = apps.get_model('cts_forms', 'Report')
        reports = Report.objects.all()
        for record in reports:
            email = record.contact_email
            if email is not None:
                record.number_contacts = len(Report.objects.filter(contact_email=email))
                record.save()
            else:
                record.number_contacts = None
                record.save()

        # quality check
        reports = Report.objects.filter(number_contacts__isnull=False)
        Old_count = apps.get_model('cts_forms', 'EmailReportCount')
        for record in reports:
            count = Old_count.objects.filter(report=record.pk)[0].email_count
            if record.number_contacts != count:
                logger.warning(f"! Email count off for {record.pk}. \n new: {record.number_contacts}\n old: {count}")
                

    operations = [
        migrations.RunPython(backfill_email_count),
    ]