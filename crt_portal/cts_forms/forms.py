from datetime import datetime

from django.core.validators import ValidationError
from django.forms import ModelForm, CheckboxInput, ChoiceField, TypedChoiceField, TextInput, EmailInput, \
    ModelMultipleChoiceField, MultipleChoiceField
from django.utils.translation import gettext_lazy as _

from .question_group import QuestionGroup
from .widgets import UsaRadioSelect, UsaCheckboxSelectMultiple, CrtRadioArea, CrtDropdown, CrtMultiSelect
from .models import Report, ProtectedClass, HateCrimesandTrafficking
from .model_variables import (
    ELECTION_CHOICES,
    RESPONDENT_TYPE_CHOICES,
    PROTECTED_CLASS_CHOICES,
    PROTECTED_CLASS_ERROR,
    PRIMARY_COMPLAINT_CHOICES,
    PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
    PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
    PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
    EMPLOYER_SIZE_CHOICES,
    SECTION_CHOICES,
    STATES_AND_TERRITORIES,
    VIOLATION_SUMMARY_ERROR,
    WHERE_ERRORS,
    HATE_CRIMES_TRAFFICKING_CHOICES,
    PRIMARY_COMPLAINT_ERROR,
    CORRECTIONAL_FACILITY_LOCATION_CHOICES,
    CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
    POLICE_LOCATION_ERRORS,
)
from .phone_regex import phone_validation_regex

import logging

logger = logging.getLogger(__name__)


class ContactA11y():
    def __init__(self):
        self.name_a11y_id = 'contact_name'
        self.contact_a11y_id = 'contact_info'

    def name_id(self):
        return self.name_a11y_id

    def contact_info_id(self):
        return self.contact_a11y_id


class Contact(ModelForm):
    class Meta:
        a11y = ContactA11y()
        model = Report
        fields = [
            'contact_first_name', 'contact_last_name',
            'contact_email', 'contact_phone'
        ]
        widgets = {
            'contact_first_name': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.name_id
            }),
            'contact_last_name': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.name_id
            }),
            'contact_email': EmailInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.contact_info_id
            }),
            'contact_phone': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.contact_info_id,
                'pattern': phone_validation_regex,
                'title': _('If you submit a phone number, please make sure to include between 7 and 15 digits. The characters "+", ")", "(", "-", and "." are allowed. Please include country code if entering an international phone number.')
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        a11y = ContactA11y()

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
                ally_id=a11y.name_id
            ),
            QuestionGroup(
                self,
                ('contact_email', 'contact_phone'),
                group_name=_('Contact information'),
                help_text=_('You are not required to provide contact information, but it will help us if we need to gather more information about the incident you are reporting or to respond to your submission'),
                ally_id=a11y.contact_info_id
            )
        ]


class PrimaryReason(ModelForm):
    class Meta:
        model = Report
        fields = [
            'primary_complaint',
            'hatecrimes_trafficking'
        ]
        widgets = {
            'hatecrimes_trafficking': UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'hatecrimes-help-text'
            }),
            'primary_complaint': CrtRadioArea,
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['primary_complaint'] = ChoiceField(
            choices=PRIMARY_COMPLAINT_CHOICES,
            widget=CrtRadioArea(attrs={
                'choices_to_examples': PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
                'choices_to_helptext': PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
            }),
            required=True,
            error_messages={
                'required': PRIMARY_COMPLAINT_ERROR
            },
            help_text=_('Please choose the option below that best fits your situation. The examples listed in each are only a sampling of related issues. You will have space to explain in detail later.')
        )

        self.fields['hatecrimes_trafficking'] = ModelMultipleChoiceField(
            queryset=HateCrimesandTrafficking.objects.filter(hatecrimes_trafficking_option__in=HATE_CRIMES_TRAFFICKING_CHOICES),
            widget=UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'hatecrimes-help-text'
            }),
            required=False,
            label=_('Please select if any that apply to your situation (optional)')
        )
        self.question_groups = [
            QuestionGroup(
                self,
                ('hatecrimes_trafficking',),
                group_name=_('Hate Crimes & Human Trafficking'),
                help_text=_('Hate crimes and human trafficking are considered criminal cases and go through a different process for investigation than other civil rights cases. If we determine your situation falls into these categories after submitting your concern, we will contact you with next steps.'),
                optional=False,
                cls="text-bold",
                ally_id="hatecrimes-help-text"
            )
        ]


class Details(ModelForm):
    class Meta:
        model = Report
        fields = [
            'violation_summary'
        ]

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['violation_summary'].widget.attrs['class'] = 'usa-textarea word-count-500'
        self.label_suffix = ''
        self.fields['violation_summary'].label = _('Tell us what happened')
        self.fields['violation_summary'].widget.attrs['aria-describedby'] = 'details-help-text'
        self.fields['violation_summary'].help_text = _("Please include any details you have about time, location, or people involved with the event, names of witnesses or any materials that would support your description")
        self.fields['violation_summary'].error_messages = {'required': VIOLATION_SUMMARY_ERROR}


class LocationForm(ModelForm):
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
            'location_name': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': 'location-help-text'
            }),
            'location_address_line_1': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': 'location-help-text'
            }),
            'location_address_line_2': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': 'location-help-text'
            }),
            'location_city_town': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': 'location-help-text'
            }),
            'location_state': CrtDropdown(attrs={
                'aria-describedby': 'location-help-text'
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

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
            label='State',
            help_text="Where did this happen?"
        )
        self.fields['location_state'].widget.attrs['list'] = 'states'

        self.question_groups = [
            QuestionGroup(
                self,
                ('location_name', 'location_address_line_1', 'location_address_line_2'),
                group_name=_('Where did this happen?'),
                help_text=_('Please be as specific as possible. We will handle this information with sensitivity.'),
                optional=False,
                ally_id='location-help-text'
            ),
        ]


class ElectionLocation(LocationForm):
    class Meta:
        model = Report
        fields = LocationForm.Meta.fields + ['election_details']
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)
        self.question_groups = [
            QuestionGroup(
                self,
                ('election_details',),
                group_name=_('What kind of election or voting activity was this related to?'),
                optional=False
            )
        ] + self.question_groups

        self.fields['election_details'] = TypedChoiceField(
            choices=ELECTION_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=True,
            error_messages={
                'required': _('Please select the type of election or voting activity.')
            }
        )


class WorkplaceLocation(LocationForm):
    class Meta:
        model = Report
        fields = LocationForm.Meta.fields + [
            'public_or_private_employer',
            'employer_size'
        ]
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)
        self.question_groups = [
            QuestionGroup(
                self,
                ('public_or_private_employer',),
                group_name=_('Was this a public or private employer?'),
                optional=False
            ),
            QuestionGroup(
                self,
                ('employer_size',),
                group_name=_('How large is this employer?'),
                optional=False
            )
        ] + self.question_groups

        self.fields['public_or_private_employer'] = TypedChoiceField(
            choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
            widget=UsaRadioSelect(attrs={
                'help_text': {
                    'public_employer': _('Funded by the government like a post office, fire department, courthouse, DMV, or public school. This could be at the local, state, or federal level'),
                    'private_employer': _('Businesses or non-profits not funded by the government such as retail stores, banks, or restaurants')
                }
            }),
            required=True,
            error_messages={
                'required': _('Please select what type of employer this is.')
            },
            label=''
        )

        self.fields['employer_size'] = TypedChoiceField(
            choices=EMPLOYER_SIZE_CHOICES,
            widget=UsaRadioSelect,
            required=True,
            error_messages={
                'required': _('Please select how large the employer is.')
            },
            label=''
        )


class PoliceLocation(LocationForm):
    class Meta:
        model = Report
        fields = LocationForm.Meta.fields + ['inside_correctional_facility', 'correctional_facility_type']
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)

        self.name = 'PoliceLocation'

        self.fields['inside_correctional_facility'] = TypedChoiceField(
            choices=CORRECTIONAL_FACILITY_LOCATION_CHOICES,
            widget=UsaRadioSelect,
            required=True,
            error_messages={
                'required': POLICE_LOCATION_ERRORS['facility']
            },
            label=''
        )

        self.fields['correctional_facility_type'] = TypedChoiceField(
            choices=CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
            widget=UsaRadioSelect,
            required=False,
            label=''
        )
        self.fields['correctional_facility_type'].widget.attrs['class'] = 'margin-bottom-0 padding-bottom-0 padding-left-1'
        self.fields['correctional_facility_type'].help_text = 'What type of prison or correctional facility?'

    def clean(self):
        inside_facility = self.cleaned_data.get('inside_correctional_facility')
        facility_type = self.cleaned_data.get('correctional_facility_type')

        if inside_facility == 'inside' and facility_type is None:
            msg = ValidationError(POLICE_LOCATION_ERRORS['facility_type'])
            self.add_error('correctional_facility_type', msg)
        else:
            self.cleaned_data['correctional_facility_type'] = None

        return self.cleaned_data


class ProtectedClassForm(ModelForm):
    class Meta:
        model = Report
        fields = ['protected_class', 'other_class']

    # Overriding __init__ here allows us to provide initial data for 'protected_class' field
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['protected_class'] = ModelMultipleChoiceField(
            error_messages={'required': PROTECTED_CLASS_ERROR},
            required=True,
            label="",
            queryset=ProtectedClass.objects.filter(protected_class__in=PROTECTED_CLASS_CHOICES).order_by('form_order'),
            widget=UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'protected-class-help-text'
            }),
        )
        self.fields['other_class'].help_text = _('Please describe "Other reason"')
        self.fields['other_class'].widget = TextInput(
            attrs={'class': 'usa-input word-count-10'}
        )

        self.question_groups = [
            QuestionGroup(
                self,
                ('protected_class',),
                group_name=_('Do you believe any of these personal characteristics influenced why you were treated this way?'),
                help_text=_('Some civil rights laws protect people from discrimination, which include these protected classes. These are some of the most common classes that we see.'),
                optional=False,
                ally_id="protected-class-help-text"
            )
        ]


class When(ModelForm):
    class Meta:
        model = Report
        fields = ['last_incident_month', 'last_incident_day', 'last_incident_year']
        widgets = {
            'last_incident_month': TextInput(attrs={
                'class': 'usa-input usa-input--small',
                'required': True,
                'type': 'number',
            }),
            'last_incident_day': TextInput(attrs={
                'class': 'usa-input usa-input--small',
                'type': 'number',
            }),
            'last_incident_year': EmailInput(attrs={
                'class': 'usa-input usa-input--medium',
                'required': True,
                'type': 'number',
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['last_incident_month'].label = _('Month')
        self.fields['last_incident_month'].error_messages = {
            'required': _('Please enter a month'),
        }
        self.fields['last_incident_day'].label = _('Day')
        self.fields['last_incident_year'].label = _('Year')
        self.fields['last_incident_year'].error_messages = {
            'required': _('Please enter a year'),
        }

    def clean(self):
        """Validating more than one field at a time can't be done in the model validation"""
        cleaned_data = super(When, self).clean()

        try:
            year = cleaned_data['last_incident_year']
            month = cleaned_data['last_incident_month']
            day = cleaned_data['last_incident_day'] or 1
            test_date = datetime(year, month, day)
            if test_date > datetime.now():
                raise ValidationError(
                    _('Date can not be in the future'),
                    params={'value': test_date.strftime('%x')},
                )
        except ValueError:
            # a bit of a catch-all for all the ways people could make bad dates
            raise ValidationError(
                _(f'Invalid date format {month}/{day}/{year}'),
                params={'value': f'{month}/{day}/{year}'},
            )
        except KeyError:
            # these will be caught by the built in error validation
            return cleaned_data

        return cleaned_data


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


class Filters(ModelForm):
    class Meta:
        model = Report
        fields = [
            'assigned_section',
            'contact_first_name',
            'contact_last_name',
            'location_city_town',
            'location_state'
        ]
        widgets = {
            'contact_first_name': TextInput(attrs={
                'class': 'usa-input'
            }),
            'contact_last_name': TextInput(attrs={
                'class': 'usa-input'
            }),
            'location_city_town': TextInput(attrs={
                'class': 'usa-input'
            }),
            'location_state': CrtDropdown
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['assigned_section'] = MultipleChoiceField(
            choices=SECTION_CHOICES,
            widget=CrtMultiSelect,
            required=False
        )
        self.fields['location_state'] = ChoiceField(
            choices=STATES_AND_TERRITORIES,
            widget=CrtDropdown,
            required=False,
        )

        self.fields['assigned_section'].label = _('View sections')
        self.fields['contact_first_name'].label = _('Contact first name')
        self.fields['contact_last_name'].label = _('Contact last name')
        self.fields['location_city_town'].label = _('City')

        self.fields['location_state'].label = _('State')
        self.fields['location_state'].widget.attrs['list'] = 'states'
