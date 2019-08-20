from django.test import TestCase

from .models import ProtectedClass, Report
from .forms import WhatHappened, Where, Who, Details, Contact

class Valad_Form_Test(TestCase):
    """Confirms each form is valid when given valid test data."""
    def test_WhatHappened_valad(self):
        form = WhatHappened(data={
            'primary_complaint': 'vote',
            'protected_class_set': ProtectedClass.objects.all(),
        })
        self.assertTrue(form.is_valid())

    def test_Where_valid(self):
        form = Where(data={
            'place': 'place_of_worship',
            'public_or_private_employer': 'public_employer',
            'employer_size': '14_or_less',
            'public_or_private_school': 'public',
            'public_or_private_facility': 'state_local_facility',
            'public_or_private_healthcare': 'state_local_facility',
        })
        self.assertTrue(form.is_valid())

    def test_Who_valad(self):
        form = Who( data={
            'respondent_contact_ask': False,
            'respondent_type': 'employer',
            'respondent_name': 'Max',
            'respondent_city': 'Hometown',
            'respondent_state': 'AK',
        })
        self.assertTrue(form.is_valid())

    def test_Details_valad(self):
        form = Details( data={
            'violation_summary': 'Hello! I have a problem.',
            'when': 'last_6_months',
            'how_many': 'no',
        })
        self.assertTrue(form.is_valid())

    def test_Contact_valad(self):
        form = Contact( data={
            'who_reporting_for': 'employer',
            'relationship': 'myself',
            'do_not_contact': '',
            'contact_given_name': 'first_name',
            'contact_family_name': 'last_name',
            'contact_email': 'email@email.com',
            'contact_state': 'CA',
            'contact_address_line_1': '123 Street',
            'contact_address_line_2': 'Apt B',
            'contact_phone': '202-222-2222',
        })
        self.assertTrue(form.is_valid())


