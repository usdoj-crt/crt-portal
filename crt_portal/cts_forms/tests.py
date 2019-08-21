from django.test import TestCase

from .models import ProtectedClass, Report
from .forms import WhatHappened, Where, Who, Details, Contact

class Valid_Form_Tests(TestCase):
    """Confirms each form is valid when given valid test data."""
    def test_WhatHappened_valid(self):
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

    def test_Who_valid(self):
        form = Who( data={
            'respondent_contact_ask': False,
            'respondent_type': 'employer',
            'respondent_name': 'Max',
            'respondent_city': 'Hometown',
            'respondent_state': 'AK',
        })
        self.assertTrue(form.is_valid())

    def test_Details_valid(self):
        form = Details( data={
            'violation_summary': 'Hello! I have a problem.',
            'when': 'last_6_months',
            'how_many': 'no',
        })
        self.assertTrue(form.is_valid())

    def test_Contact_valid(self):
        form = Contact( data={
            'who_reporting_for': 'myself',
            'relationship': 'parent_guardian',
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


class Validation_Form_Tests(TestCase):
    """Confirming validation on the server level"""
    def test_required_primary_complaint(self):
        form = WhatHappened(data={
            'primary_complaint': '',
            'protected_class_set': ProtectedClass.objects.all(),
        })

        self.assertTrue('primary_complaint<ul class="errorlist"><li>This field is required.' in str(form.errors))

    def test_required_who_reporting_for(self):
        form = Contact( data={
            'who_reporting_for': '',
            'relationship': 'parent_guardian',
            'do_not_contact': '',
            'contact_given_name': 'first_name',
            'contact_family_name': 'last_name',
            'contact_email': 'email@email.com',
            'contact_state': 'CA',
            'contact_address_line_1': '123 Street',
            'contact_address_line_2': 'Apt B',
            'contact_phone': '202-222-2222',
        })
        self.assertTrue('who_reporting_for<ul class="errorlist"><li>This field is required.' in str(form.errors))


    def test_required_when(self):
        form = Details( data={
            'violation_summary': 'Hello! I have a problem.',
            'when': '',
            'how_many': 'no',
        })
        self.assertTrue('when<ul class="errorlist"><li>This field is required.' in str(form.errors))


    def test_required_violation_summary(self):
        form = Details( data={
            'violation_summary': '',
            'when': 'last_6_months',
            'how_many': 'no',
        })
        self.assertTrue('violation_summary<ul class="errorlist"><li>This field is required.' in str(form.errors))

    def test_required_when(self):
        form = Details( data={
            'violation_summary': 'Hello! I have a problem.',
            'when': '',
            'how_many': 'no',
        })
        self.assertTrue('when<ul class="errorlist"><li>This field is required.' in str(form.errors))
