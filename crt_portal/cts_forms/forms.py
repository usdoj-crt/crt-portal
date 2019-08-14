from django.forms import ModelForm, RadioSelect, Select, ModelMultipleChoiceField, CheckboxSelectMultiple, CheckboxInput

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

        # Overriding save allows us to process the value of 'protected_class' field
    def save(self, commit=True):
        # Get the unsave ProtectedClass instance
        instance = forms.ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m
        def save_m2m():
           old_save_m2m()
           instance.protected_class_set.clear()
           instance.protected_class_set.add(*self.cleaned_data['protected_class'])
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


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

    def __init__(self, *args, **kwargs):
        """setting label settings to remove --- in the selects"""
        super(Where, self).__init__(*args, **kwargs)
        self.fields['place'].empty_label = None
        self.fields['public_or_private_employer'].empty_label = None
        self.fields['employer_size'].empty_label = None
        self.fields['public_or_private_school'].empty_label = None
        self.fields['public_or_private_facility'].empty_label = None
        self.fields['public_or_private_healthcare'].empty_label = None


class Who(ModelForm):
    class Meta:
        model = Report
        respondent_state = ModelMultipleChoiceField(queryset=StatesAndTerritories.objects.all())
        fields = ['respondent_contact_ask', 'respondent_type', 'respondent_name', 'respondent_city', 'respondent_state']
        widgets = {
            'respondent_contact_ask': CheckboxInput,
            'respondent_type': RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['respondent_state'] = [t.pk for t in kwargs['instance'].respondent_state_set.all()]

        ModelForm.__init__(self, *args, **kwargs)


    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m
        def save_m2m():
           old_save_m2m()
           instance.state_set.clear()
           instance.state_set.add(*self.cleaned_data['respondent_state'])
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance



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
        contact_state = ModelMultipleChoiceField(queryset=StatesAndTerritories.objects.all())
        fields = ['who_reporting_for', 'relationship', 'do_not_contact', 'contact_given_name', 'contact_family_name', 'contact_email', 'contact_state', 'contact_address_line_1', 'contact_address_line_2', 'contact_phone']
        widgets = {
            'do_not_contact': CheckboxInput,
            'who_reporting_for': RadioSelect,
            'relationship': RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['contact_state'] = [t.pk for t in kwargs['instance'].respondent_state_set.all()]

        ModelForm.__init__(self, *args, **kwargs)

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m
        def save_m2m():
           old_save_m2m()
           instance.state_set.clear()
           instance.state_set.add(*self.cleaned_data['contact_state'])
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance

