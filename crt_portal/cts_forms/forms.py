from datetime import datetime

from django.core.validators import ValidationError
from django.forms import ModelForm, ChoiceField, TypedChoiceField, TextInput, EmailInput, \
    ModelMultipleChoiceField, MultipleChoiceField, Select
from django.utils.translation import gettext_lazy as _

from .question_group import QuestionGroup
from .widgets import UsaRadioSelect, UsaCheckboxSelectMultiple, CrtPrimaryIssueRadioGroup, CrtMultiSelect, ComplaintSelect
from .models import Report, ProtectedClass, HateCrimesandTrafficking
from .model_variables import (
    ELECTION_CHOICES,
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
    SERVICEMEMBER_CHOICES,
    SERVICEMEMBER_ERROR,
    CORRECTIONAL_FACILITY_LOCATION_CHOICES,
    CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
    POLICE_LOCATION_ERRORS,
    COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
    COMMERCIAL_OR_PUBLIC_PLACE_HELP_TEXT,
    PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
    STATUS_CHOICES,
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
            'contact_email', 'contact_phone', 'servicemember',
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
        self.fields['servicemember'] = TypedChoiceField(
            error_messages={'required': SERVICEMEMBER_ERROR},
            widget=UsaRadioSelect(),
            label=_('Are you now or have ever been an active duty service member?'),
            help_text=_('If you’re reporting on behalf of someone else, please select their status.'),
            empty_value=None,
            choices=SERVICEMEMBER_CHOICES,
        )
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
            'primary_complaint'
        ]
        widgets = {
            'primary_complaint': CrtPrimaryIssueRadioGroup
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['primary_complaint'] = ChoiceField(
            choices=PRIMARY_COMPLAINT_CHOICES,
            widget=CrtPrimaryIssueRadioGroup(attrs={
                'choices_to_examples': PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
                'choices_to_helptext': PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
            }),
            required=True,
            error_messages={
                'required': PRIMARY_COMPLAINT_ERROR
            },
            label=_('What is your primary reason for contacting the Civil Rights Division?'),
            help_text=_('Select the reason that best describes your concern. Each reason lists examples of civil rights violations that may relate to your incident. In another section of this report, you will be able to describe your concern in your own words.'),
        )


class HateCrimesTrafficking(ModelForm):
    class Meta:
        model = Report
        fields = [
            'hatecrimes_trafficking'
        ]
        widgets = {
            'hatecrimes_trafficking': UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'hatecrimes-help-text'
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['hatecrimes_trafficking'] = ModelMultipleChoiceField(
            queryset=HateCrimesandTrafficking.objects.filter(hatecrimes_trafficking_option__in=HATE_CRIMES_TRAFFICKING_CHOICES),
            widget=UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'hatecrimes-help-text'
            }),
            required=False,
            label=_('Please select if any apply to your concern (optional)')
        )

        self.question_groups = [
            QuestionGroup(
                self,
                ('hatecrimes_trafficking',),
                group_name=_('Hate crimes & human trafficking'),
                help_text=_('Please let us know if you would describe your concern as either a hate crime or human trafficking. This information can help us take action against these types of violations. We will contact you about the next steps. We also encourage you to contact law enforcement if you or someone else is in immediate danger.'),
                optional=False,
                label_cls="margin-bottom-4",
                help_cls="text-bold",
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
        self.fields['violation_summary'].required = True


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
            'location_state': Select(attrs={
                'aria-describedby': 'location-help-text',
                'class': 'usa-select'
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
        self.fields['location_name'].required = True
        self.fields['location_address_line_1'].label = 'Street address 1 (Optional)'
        self.fields['location_address_line_2'].label = 'Street address 2 (Optional)'
        self.fields['location_city_town'].label = 'City/town'
        self.fields['location_city_town'].error_messages = {
            'required': errors['location_city_town']
        }
        self.fields['location_city_town'].required = True
        self.fields['location_state'] = ChoiceField(
            choices=(('', _(' ')),) + STATES_AND_TERRITORIES,
            widget=Select(attrs={
                'aria-describedby': 'location-help-text',
                'class': 'usa-select'
            }),
            required=True,
            error_messages={
                'required': errors['location_state']
            },
            label='State',
            help_text="Where did this happen?",
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
            widget=UsaRadioSelect(attrs={
                'help_text': {
                    'federal': _('Presidential or congressional'),
                    'state_local': _('Governor, state legislation, city position (mayor, council, local board)'),
                    'both': _('Federal & State/local')
                }
            }),
            required=True,
            error_messages={
                'required': _('Please select the type of election or voting activity.')
            },
            label=''
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


class CommercialPublicLocation(LocationForm):
    class Meta:
        model = Report
        fields = LocationForm.Meta.fields + ['commercial_or_public_place', 'other_commercial_or_public_place']
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)

        self.name = 'CommericalPublicLocation'

        self.fields['commercial_or_public_place'] = TypedChoiceField(
            choices=COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect(attrs={
                'help_text': COMMERCIAL_OR_PUBLIC_PLACE_HELP_TEXT
            }),
            required=True,
            error_messages={
                'required': _('Please select the type of location. If none of these apply to your situation, please select "Other".')
            }
        )

        self.fields['other_commercial_or_public_place'].help_text = _('Please describe')
        self.fields['other_commercial_or_public_place'].widget = TextInput(
            attrs={'class': 'usa-input word-count-10'}
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

        if inside_facility == 'inside':
            if bool(facility_type) is False:
                msg = ValidationError(POLICE_LOCATION_ERRORS['facility_type'])
                self.add_error('correctional_facility_type', msg)

        if inside_facility == 'outside':
            self.cleaned_data['correctional_facility_type'] = None

        return self.cleaned_data


class EducationLocation(LocationForm):
    class Meta:
        model = Report
        fields = LocationForm.Meta.fields + ['public_or_private_school']
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)

        self.question_groups = [
            QuestionGroup(
                self,
                ('public_or_private_school',),
                group_name=_('Did this happen at a public or a private school, educational program or activity?'),
                help_text=_('Includes schools, educational programs, or educational activities, like training programs, sports teams, clubs, or other school-sponsored activities'),
                optional=False,
                ally_id='education-location-help-text'
            ),
        ] + self.question_groups

        self.fields['public_or_private_school'] = TypedChoiceField(
            choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
            widget=UsaRadioSelect(attrs={
                'aria-describedby': 'education-location-help-text'
            }),
            label='',
            required=True,
            error_messages={
                'required': _('Please select the type of school or educational program.')
            }
        )


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
                help_text=_('There are federal and state laws that protect people from discrimination based on their personal characteristics. Here is a list of the most common characteristics that are legally protected. Select any that apply to your incident.'),
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
            'required': _('Please enter a month.'),
        }
        self.fields['last_incident_month'].required = True
        self.fields['last_incident_day'].label = _('Day')
        self.fields['last_incident_year'].label = _('Year')
        self.fields['last_incident_year'].error_messages = {
            'required': _('Please enter a year.'),
        }
        self.fields['last_incident_year'].required = True

    def clean(self):
        """Validating more than one field at a time can't be done in the model validation"""
        cleaned_data = super(When, self).clean()

        try:
            year = cleaned_data['last_incident_year']
            month = cleaned_data['last_incident_month']
            day = cleaned_data['last_incident_day'] or 1
            test_date = datetime(year, month, day)
            if test_date > datetime.now():
                self.add_error('last_incident_year', ValidationError(
                    _('Date can not be in the future.'),
                    params={'value': test_date.strftime('%x')},
                ))
            if year < 100:
                self.add_error('last_incident_year', ValidationError(
                    _('Please enter four digits for the year.'),
                    params={'value': test_date.strftime('%x')},
                ))
            if test_date < datetime(1899, 12, 31):
                self.add_error('last_incident_year', ValidationError(
                    _('Please enter a year after 1900.'),
                    params={'value': test_date.strftime('%x')},
                ))
        except ValueError:
            # a bit of a catch-all for all the ways people could make bad dates
            self.add_error('last_incident_year', ValidationError(
                _(f'Invalid date format {month}/{day}/{year}.'),
                params={'value': f'{month}/{day}/{year}'},
            ))
        except KeyError:
            # these will be caught by the built in error validation
            return cleaned_data

        return cleaned_data


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
                'class': 'usa-input',
                'name': 'contact_first_name'
            }),
            'contact_last_name': TextInput(attrs={
                'class': 'usa-input',
                'name': 'contact_last_name'
            }),
            'location_city_town': TextInput(attrs={
                'class': 'usa-input',
                'name': 'location_city_town'
            }),
            'location_state': Select(attrs={
                'name': 'location_state',
                'class': 'usa-select'
            })
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['assigned_section'] = MultipleChoiceField(
            choices=SECTION_CHOICES,
            widget=CrtMultiSelect(attrs={
                'classes': 'text-uppercase',
                'name': 'assigned_section'
            }),
            required=False
        )
        self.fields['location_state'] = ChoiceField(
            choices=STATES_AND_TERRITORIES,
            widget=Select(attrs={
                'name': 'location_state',
                'class': 'usa-select'
            }),
            required=False,
        )

        self.fields['assigned_section'].label = _('View sections')
        self.fields['contact_first_name'].label = _('Contact first name')
        self.fields['contact_last_name'].label = _('Contact last name')
        self.fields['location_city_town'].label = _('Incident location city')

        self.fields['location_state'].label = _('Incident location state')


class ComplaintActions(ModelForm):
    class Meta:
        model = Report
        fields = ['assigned_section', 'status']

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['assigned_section'] = ChoiceField(
            widget=ComplaintSelect(label='Section', attrs={
                'classes': 'text-uppercase'
            }),
            choices=SECTION_CHOICES,
            required=False
        )

        self.fields['status'] = ChoiceField(
            widget=ComplaintSelect(label='Status'),
            choices=STATUS_CHOICES,
            required=False
        )
