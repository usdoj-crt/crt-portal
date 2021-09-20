from django.test import TestCase
from .factories import ReportFactory
from ..utils import update_email_count


class Test_Helper_Utilities(TestCase):
    def setUp(self):
        ReportFactory.create(contact_email='')
        ReportFactory.create(contact_email='person1@usa.gov')
        ReportFactory.create_batch(3, contact_email='person2@usa.gov')

    def test_update_email_count(self):
        self.assertTrue(update_email_count(None) is None)
        self.assertTrue(update_email_count('person1@usa.gov') == 1)
        self.assertTrue(update_email_count('person2@usa.gov') == 3)
