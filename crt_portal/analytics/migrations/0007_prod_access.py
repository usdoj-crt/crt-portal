import os

from django.db import migrations
from django.conf import settings

from analytics import models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0006_staging_access'),
    ]

    if settings.TESTING:
        # The analytics user isn't needed for tests, and having the tests try to create it can break local development.
        operations = []
    elif os.environ.get('ENV', 'UNDEFINED') in ['PRODUCTION']:
        operations = models.make_analytics_user()
    else:
        operations = []
