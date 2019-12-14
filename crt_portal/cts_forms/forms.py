from django.forms import ModelForm, CheckboxInput, ChoiceField, TypedChoiceField, TextInput, EmailInput, \
    ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _
from .question_group import QuestionGroup
from .widgets import UsaRadioSelect, UsaCheckboxSelectMultiple, CrtRadioArea, CrtDropdown
from .models import Report, ProtectedClass
from .model_variables import (
    RESPONDENT_TYPE_CHOICES,
    PROTECTED_CLASS_CHOICES,
    PROTECTED_CLASS_ERROR,
    PRIMARY_COMPLAINT_CHOICES,
    PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
    PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
    STATES_AND_TERRITORIES,
    VIOLATION_SUMMARY_ERROR,
    WHERE_ERRORS
)
from .phone_regex import phone_validation_regex

import logging

logger = logging.getLogger(__name__)


class Contact(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.label_suffix = ''

        self.fields['contact_first_name'].label = _('First name')
        self.fields['contact_last_name'].label = _('Last name')
        self.fields['contact_email'].label = _('Email address')
        self.fields['contact_phone'].label = _('Phone number')

        self.question_groups = [
            QuestionGroup(
                self,
                ('contact_first_name', 'contact_last_name'),
                group_name=_('Your name'),
                help_text=_('Leave the fields blank if you\'d like to file anonymously'),
            ),
            QuestionGroup(
                self,
                ('contact_email', 'contact_phone'),
                group_name=_('Contact information'),
                help_text=_('You are not required to provide contact information, but it will help us if we need to gather more information about the incident you are reporting or to respond to your submission'),
            )
        ]

    class Meta:
        model = Report
        fields = [
            'contact_first_name', 'contact_last_name',
            'contact_email', 'contact_phone'
        ]
        widgets = {
            'contact_first_name': TextInput(attrs={'class': 'usa-input'}),
            'contact_last_name': TextInput(attrs={'class': 'usa-input'}),
            'contact_email': EmailInput(attrs={'class': 'usa-input'}),
            'contact_phone': TextInput(attrs={
                'class': 'usa-input',
                'pattern': phone_validation_regex,
                'title': _('If you submit a phone number, please make sure to include between 7 and 15 digits. The characters "+", ")", "(", "-", and "." are allowed. Please include country code if entering an international phone number.')
            }),
        }


class PrimaryReason(ModelForm):
    primary_complaint = ChoiceField(
        choices=PRIMARY_COMPLAINT_CHOICES,
        widget=CrtRadioArea(attrs={
            'choices_to_examples': PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
            'choices_to_helptext': PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
        }),
        required=True,
        error_messages={
            'required': _('Please select a primary reason to continue.')
        },
        help_text=_('Please choose the option below that best fits your situation. The examples listed in each are only a sampling of related issues. You will have space to explain in detail later.')
    )

    class Meta:
        model = Report
        fields = [
            'primary_complaint'
        ]


class Details(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['violation_summary'].widget.attrs['class'] = 'usa-textarea word-count-500'
        self.label_suffix = ''
        self.fields['violation_summary'].label = _('Tell us what happened')
        self.fields['violation_summary'].widget.attrs['aria-describedby'] = 'word_count_area'
        self.fields['violation_summary'].help_text = _("Please include any details you have about time, location, or people involved with the event, names of witnesses or any materials that would support your description")
        self.fields['violation_summary'].error_messages = {'required': VIOLATION_SUMMARY_ERROR}

    class Meta:
        model = Report
        fields = [
            'violation_summary'
        ]


class LocationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        errors = dict(WHERE_ERRORS)

        self.fields['location_name'].label = 'Location name'
        self.fields['location_name'].help_text = 'Examples: Name of business, school, intersection, prison, polling place, website, etc.'
        self.fields['location_name'].error_messages = {
            'required': errors['location_name']
        }
        self.fields['location_address_line_1'].label = 'Street address 1 (Optional)'
        self.fields['location_address_line_2'].label = 'Street address 2 (Optional)'
        self.fields['location_city_town'].label = 'City/town'
        self.fields['location_city_town'].error_messages = {
            'required': errors['location_city_town']
        }
        self.fields['location_state'] = ChoiceField(
            choices=STATES_AND_TERRITORIES,
            widget=CrtDropdown,
            required=True,
            error_messages={
                'required': errors['location_state']
            },
            label='State'
        )

        self.question_groups = [
            QuestionGroup(
                self,
                ('location_name', 'location_address_line_1', 'location_address_line_2'),
                group_name='Where did this happen?',
                help_text='Please be as specific as possible. We will handle this information with sensitivity.',
                optional=False
            )
        ]

    class Meta:
        model = Report
        fields = [
            'location_name',
            'location_address_line_1',
            'location_address_line_2',
            'location_city_town',
            'location_state',
        ]

        widgets = {
            'location_name': TextInput(attrs={'class': 'usa-input'}),
            'location_address_line_1': TextInput(attrs={'class': 'usa-input'}),
            'location_address_line_2': TextInput(attrs={'class': 'usa-input'}),
            'location_city_town': TextInput(attrs={'class': 'usa-input'}),
            'location_state': CrtDropdown,
        }


class ProtectedClassForm(ModelForm):
    class Meta:
        model = Report
        fields = ['protected_class', 'other_class']

    # Overriding __init__ here allows us to provide initial data for 'protected_class' field
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['protected_class'] = ModelMultipleChoiceField(
            label=_('Do you believe any of these personal characteristics influenced why you were treated this way?'),
            help_text=_('Some civil rights laws protect people from discrimination, which include these protected classes. These are some of the most common classes that we see.'),
            error_messages={'required': PROTECTED_CLASS_ERROR},
            required=True,
            queryset=ProtectedClass.objects.filter(protected_class__in=PROTECTED_CLASS_CHOICES).order_by('form_order'),
            widget=UsaCheckboxSelectMultiple,
        )
        self.fields['other_class'].help_text = _('Please describe "Other reason"')
        self.fields['other_class'].widget = TextInput(
            attrs={'class': 'usa-input word-count-10'}
        )


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
