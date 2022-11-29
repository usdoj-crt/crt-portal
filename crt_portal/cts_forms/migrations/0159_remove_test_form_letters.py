from django.db import migrations
import logging

logger = logging.getLogger(__name__)


def remove_test_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model('cts_forms', 'ResponseTemplate')
    test_hce_templates = ResponseTemplate.objects.filter(title__icontains='(TEST) HCE - Form Letter')
    for test_hce_template in test_hce_templates:
        test_hce_template.delete()
        logger.info(f'Deleted HCE TEST form letter:{test_hce_template.title}')

def revert_function(apps, schema_editor):
   #  We no longer add form letters this way, so we don't want to add them here.
   #  We do want to be able to revert this migration though.
   pass

class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0158_alter_repeatwriterinfo_table'),
    ]

    operations = [
        migrations.RunPython(remove_test_templates, revert_function),
    ]
