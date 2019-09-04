from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple, CheckboxInput, TypedChoiceField

from .widgets import UsaRadioSelect
from .models import Report, ProtectedClass
from .model_variables import EMPLOYER_SIZE_CHOICES, PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, RESPONDENT_TYPE_CHOICES, HOW_MANY_CHOICES, RELATIONSHIP_CHOICES, PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, PUBLIC_OR_PRIVATE_FACILITY_CHOICES, PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES

import logging

logger = logging.getLogger(__name__)


class WhatHappened(ModelForm):
    class Meta:
        model = Report
        protected_class = ModelMultipleChoiceField(
            queryset=ProtectedClass.objects.all()
        )
        fields = ['primary_complaint', 'protected_class']
        widgets = {
            'primary_complaint': UsaRadioSelect,
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
    public_or_private_employer = TypedChoiceField(
        choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )
    public_or_private_facility = TypedChoiceField(
        choices=PUBLIC_OR_PRIVATE_FACILITY_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )
    public_or_private_healthcare = TypedChoiceField(
        choices=PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )
    employer_size = TypedChoiceField(
        choices=EMPLOYER_SIZE_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )
    public_or_private_school = TypedChoiceField(
        choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )

    class Meta:
        model = Report
        fields = ['place', 'public_or_private_employer', 'employer_size', 'public_or_private_school', 'public_or_private_facility', 'public_or_private_healthcare']
        widgets = {
            'place': UsaRadioSelect,
        }


class Who(ModelForm):
    respondent_type = TypedChoiceField(
        choices=RESPONDENT_TYPE_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )

    class Meta:
        model = Report
        fields = ['respondent_contact_ask', 'respondent_type', 'respondent_name', 'respondent_city', 'respondent_state']
        widgets = {
            'respondent_contact_ask': CheckboxInput,
        }


class Details(ModelForm):
    how_many = TypedChoiceField(
        choices=HOW_MANY_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )

    class Meta:
        model = Report
        fields = ['violation_summary', 'when', 'how_many']
        widgets = {
            'when': UsaRadioSelect,
        }


class Contact(ModelForm):
    relationship = TypedChoiceField(
        choices=RELATIONSHIP_CHOICES, empty_value=None, widget=UsaRadioSelect, required=False
    )

    class Meta:
        model = Report
        fields = ['who_reporting_for', 'relationship', 'do_not_contact', 'contact_given_name', 'contact_family_name', 'contact_email', 'contact_state', 'contact_address_line_1', 'contact_address_line_2', 'contact_phone']
        widgets = {
            'do_not_contact': CheckboxInput,
            'who_reporting_for': UsaRadioSelect,
        }
