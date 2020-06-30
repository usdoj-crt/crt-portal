"""
WSGI config for crt_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import json
import logging

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crt_portal.settings')

logger = logging.getLogger(__name__)


def get_newrelic_key():
    """
    If we're in the cloud,
    Retrieve new relic license key from VCAP_SERVICES
    """
    environment = os.environ.get('ENV', 'UNDEFINED')
    if environment in ['STAGE', 'DEVELOP', 'PRODUCTION']:
        vcap = json.loads(os.environ['VCAP_SERVICES'])
        for service in vcap['user-provided']:
            if service['instance_name'] == "VCAP_SERVICES":
                return service['credentials']['NEW_RELIC_LICENSE_KEY']


def initialize_newrelic():
    """Initialize NewRelic instrumentation if we have a key"""
    license_key = get_newrelic_key()

    if license_key:
        import newrelic.agent
        logger.info('New Relic key found, initializing...')
        settings = newrelic.agent.global_settings()
        settings.license_key = license_key
        newrelic.agent.initialize()
        logger.info('New Relic initialized')


initialize_newrelic()

application = get_wsgi_application()
