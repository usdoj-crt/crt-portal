from django.test import TestCase

from crt_portal.wsgi import initialize_newrelic
import os


class WSGI(TestCase):

    def test_get_newrelic_key(self):
        """
        Test to make sure RewRelic can be initialized in the cloud
        """
        os.environ['ENV'] = "STAGE"
        os.environ['VCAP_SERVICES'] = """{
            "user-provided":
            [{
                "instance_name": "VCAP_SERVICES",
                "credentials":
                {
                    "NEW_RELIC_LICENSE_KEY": "1234"
                }
            }]
        }"""
        initialize_newrelic()
