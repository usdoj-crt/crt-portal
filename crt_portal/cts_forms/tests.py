import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import ProtectedClass, Report


class MyTests(TestCase):
    # all tests must start with the word test
    def test_has_required_fields(self):
        response = self.client.post("/report/", {'primary_complaint': 'vote', 'place': 'Null', 'public_or_private_employer': 'Null', 'employer_size': 'Null', 'public_or_private_school': 'Null', 'public_or_private_facility': 'Null', 'public_or_private_healthcare': 'Null', 'respondent_contact_ask': 'Null', 'respondent_type': 'Null', 'respondent_name': 'Null', 'respondent_city': 'Null', 'respondent_state': 'Null', 'violation_summary': 'Hello!', 'when': 'Null', 'how_many': 'Null', 'who_reporting_for': 'Null', 'relationship': 'Null', 'do_not_contact': 'Null', 'contact_given_name': 'Null', 'contact_family_name': 'Null', 'contact_email': 'Null', 'contact_state': 'Null', 'contact_address_line_1': 'Null', 'contact_address_line_2': 'Null', 'contact_phone': 'Null', 'protected_class': '<QuerySet []>'})
        print(response)
        self.assertFormError(response, 'form', 'something', 'This field is required.')

    # primary complaint
    # summary
