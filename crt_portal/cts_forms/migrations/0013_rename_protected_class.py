from django.db import migrations, models
from cts_forms.models import ProtectedClass
from cts_forms.model_variables import PROTECTED_CLASS_CHOICES

import logging

logger = logging.getLogger(__name__)


class Migration(migrations.Migration):

    dependencies = [
        ('cts_forms', '0010_protectedclass_form_order'),
    ]

    def retrieve_or_create_options(*args, **defaults):
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='Immigration/citizenship status (choosing this does not share your status)').update(protected_class='Immigration/citizenship status (choosing this will not share your status)')
        except:  # noqa
            logger.info('old name for immigration not detected')
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='National Origin (including ancestry, ethnicity, and language)').update(protected_class='National origin (including ancestry, ethnicity, and language)')
            c.update()
        except:  # noqa
            logger.info('old name for national origin not detected')
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='Disability (including temporary or in recovery)').update(protected_class='Disability (including temporary or recovery)')
        except:  # noqa
            logger.info('old name for disability not detected')
        try:
            with transaction.atomic():
                c = ProtectedClass.objects.filter(protected_class='Other').update(protected_class='Other reason')
        except:  # noqa
            logger.info('old name for other not detected')

    operations = [
        migrations.RunPython(retrieve_or_create_options),
    ]
