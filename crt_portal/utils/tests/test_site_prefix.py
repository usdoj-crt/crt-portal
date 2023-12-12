from utils import site_prefix
import os
from unittest import TestCase, mock


class SitePrefixTests(TestCase):
    def test_local_prefix(self):
        with mock.patch.dict(os.environ, {'ENV': 'LOCAL'}):
            self.assertEqual(site_prefix.get_site_prefix(False), 'http://localhost:8000')
            self.assertEqual(site_prefix.get_site_prefix(True), 'http://localhost:8000')

    def test_dev_prefix(self):
        with mock.patch.dict(os.environ, {'ENV': 'DEVELOP'}):
            self.assertEqual(site_prefix.get_site_prefix(False), 'https://crt-portal-django-dev.app.cloud.gov')
            self.assertEqual(site_prefix.get_site_prefix(True), 'https://crt-portal-django-dev.app.cloud.gov')

    def test_stage_prefix(self):
        with mock.patch.dict(os.environ, {'ENV': 'STAGE'}):
            self.assertEqual(site_prefix.get_site_prefix(False), 'https://crt-portal-django-stage.app.cloud.gov')
            self.assertEqual(site_prefix.get_site_prefix(True), 'https://crt-portal-django-stage.app.cloud.gov')

    def test_prod_prefix(self):
        with mock.patch.dict(os.environ, {'ENV': 'PRODUCTION'}):
            self.assertEqual(site_prefix.get_site_prefix(False), 'https://civilrights.justice.gov')
            self.assertEqual(site_prefix.get_site_prefix(True), 'https://crt-portal-django-prod.app.cloud.gov')
