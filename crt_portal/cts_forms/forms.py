from django.forms import ModelForm, RadioSelect, Select, ModelMultipleChoiceField

from .models import Report, ProtectedClass, StatesAndTerritories

import logging

logger = logging.getLogger(__name__)

class WhatHappened(ModelForm):
    class Meta:
        model = Report
        protected_class = ModelMultipleChoiceField(queryset=ProtectedClass.objects.all())
        fields = ['primary_complaint', 'protected_class']
        widgets = {
            'primary_complaint': RadioSelect,
        }
        logger.error('protected_class')


    def __init__(self, *args, **kwargs):
        # Only in case we build the form from an instance
        if kwargs.get('instance'):
            # We get the 'initial' keyword argument or initialize it
            # as a dict if it didn't exist.
            initial = kwargs.setdefault('initial', {})
            # The widget for a ModelMultipleChoiceField expects
            # a list of primary key for the selected data.
            initial['protected_class'] = [t.pk for t in kwargs[instance].protected_class_set.all()]
            logger.error(initial['protected_class'])
            logger.error('hola')

        ModelForm.__init__(self, *args, **kwargs)




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
