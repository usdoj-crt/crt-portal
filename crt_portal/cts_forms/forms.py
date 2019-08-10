from django.forms import ModelForm

from .models import Report


class WhatHappened(ModelForm):
    class Meta:
        model = Report
        fields = ['primary_complaint', 'protected_class']


class Where(ModelForm):
    class Meta:
        model = Report
        fields = ['place', 'public_or_private_employer', 'employer_size', 'public_or_private_school', 'public_or_private_facility', 'public_or_private_healthcare']


class Who(ModelForm):
    class Meta:
        model = Report
        fields = ['respondent_contact_ask', 'respondent_type', 'respondent_name', 'respondent_city', 'respondent_state']


class Details(ModelForm):
    class Meta:
        model = Report
        fields = ['violation_summary', 'when', 'how_many']


class Contact(ModelForm):
    class Meta:
        model = Report
        fields = ['who_reporting_for', 'relationship', 'do_not_contact', 'contact_given_name', 'contact_family_name', 'contact_email', 'contact_state', 'contact_address_line_1', 'contact_address_line_2', 'contact_phone']
