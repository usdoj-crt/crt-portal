import copy

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import ProtectedClass, Report
from django.forms import ModelForm, models


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class ReportTests(object):
    """" See django form wizard tests for testing examples: https://github.com/django/django-formtools/blob/master/tests/wizard/wizardtests/tests.py """
    def setUp(self):
        self.testuser, created = User.objects.get_or_create(username='testuser1')
        # Get new step data, since we modify it during the tests.
        self.wizard_step_data = copy.deepcopy(self.wizard_step_data)
        self.wizard_step_data[0]['form1-user'] = self.testuser.pk


    def test_report_form_minium(self):
        """ This example has the minimum amount of data required for a successful report"""

        what_happened_form = {
            'primary_complaint': 'vote',
            'protected_class': '<QuerySet []>',
        }

        where_form = {
            'place': 'Null',
            'public_or_private_employer': 'Null',
            'employer_size': 'Null',
            'public_or_private_school': 'Null',
            'public_or_private_facility': 'Null',
            'public_or_private_healthcare': 'Null',
        }

        who_form = {
            'respondent_contact_ask': 'Null',
            'respondent_type': 'Null',
            'respondent_name': 'Null',
            'respondent_city': 'Null',
            'respondent_state': 'Null',
        }

        details_form = {
            'violation_summary': 'Hello! I have a problem.',
            'when': 'Null',
            'how_many': 'Null',
        }

        contact_form = {
            'who_reporting_for': 'Null',
            'relationship': 'Null',
            'do_not_contact': 'Null',
            'contact_given_name': 'Null',
            'contact_family_name': 'Null',
            'contact_email': 'Null',
            'contact_state': 'Null',
            'contact_address_line_1': 'Null',
            'contact_address_line_2': 'Null',
            'contact_phone': 'Null',
        }

        FORM_STEPS_DATA = [what_happened_form, where_form, who_form, details_form, contact_form]

        for step, data_step in enumerate(FORM_STEPS_DATA, 1):
            response = self.client.post(reverse('crt_report_form'), data_step)

            if step == len(FORM_STEPS_DATA):
                self.assertEqual(response.status_code, 200)

