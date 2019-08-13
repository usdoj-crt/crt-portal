from django.forms import ModelForm, RadioSelect

from .models import Report


class WhatHappened(ModelForm):
    class Meta:
        model = Report
        fields = ['primary_complaint', 'protected_class']
        widgets = {
            'primary_complaint': RadioSelect,
            'primary_complaint': RadioSelect,
        }


class Where(ModelForm):
    class Meta:
        model = Report
        fields = ['place', 'public_or_private_employer', 'employer_size', 'public_or_private_school', 'public_or_private_facility', 'public_or_private_healthcare']
        widgets = {
            'place': RadioSelect,
            'public_or_private_employer': RadioSelect,
            'employer_size': RadioSelect,
            'public_or_private_school': RadioSelect,
            'public_or_private_facility': RadioSelect,
            'public_or_private_healthcare': RadioSelect,
        }


class Who(ModelForm):
    class Meta:
        model = Report
        fields = ['respondent_contact_ask', 'respondent_type', 'respondent_name', 'respondent_city', 'respondent_state']
        widgets = {
            'respondent_type': RadioSelect,
        }


class Details(ModelForm):
    class Meta:
        model = Report
        fields = ['violation_summary', 'when', 'how_many']
        widgets = {
            'when': RadioSelect,
            'how_many': RadioSelect,
        }


class Contact(ModelForm):
    class Meta:
        model = Report
        fields = ['who_reporting_for', 'relationship', 'do_not_contact', 'contact_given_name', 'contact_family_name', 'contact_email', 'contact_state', 'contact_address_line_1', 'contact_address_line_2', 'contact_phone']
        widgets = {
            'relationship': RadioSelect,
        }
