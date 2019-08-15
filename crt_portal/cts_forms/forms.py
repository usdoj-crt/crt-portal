from django.forms import ModelForm, RadioSelect, Select, ModelMultipleChoiceField, CheckboxSelectMultiple, CheckboxInput

from .models import Report, ProtectedClass

import logging

logger = logging.getLogger(__name__)


class WhatHappened(ModelForm):
    class Meta:
        model = Report
        protected_class = ModelMultipleChoiceField(queryset=ProtectedClass.objects.all())
        fields = ['primary_complaint', 'protected_class']
        widgets = {
            'primary_complaint': RadioSelect,
            'protected_class': CheckboxSelectMultiple,
        }

    # Overriding __init__ here allows us to provide initial
    # data for 'protected_class' field
    def __init__(self, *args, **kwargs):
        # Only in case we build the form from an instance
        # (otherwise, 'protected class' list should be empty)
        if kwargs.get('instance'):
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            # The widget for a ModelMultipleChoiceField expects
            # a list of primary key for the selected data.
            initial['protected_class'] = [t.pk for t in kwargs['instance'].protected_class_set.all()]

        ModelForm.__init__(self, *args, **kwargs)


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
            'respondent_contact_ask': CheckboxInput,
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
            'do_not_contact': CheckboxInput,
            'who_reporting_for': RadioSelect,
            'relationship': RadioSelect,
        }
