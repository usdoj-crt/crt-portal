from datetime import datetime

from django.core.validators import ValidationError
from django.forms import ModelForm, ChoiceField, TypedChoiceField, TextInput, EmailInput, \
    ModelMultipleChoiceField, Select
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
    CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
    CORRECTIONAL_FACILITY_LOCATION_CHOICES,
    POLICE_LOCATION_ERRORS,
    COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
    COMMERCIAL_OR_PUBLIC_PLACE_HELP_TEXT,
    PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
    STATUS_CHOICES,
    EMPTY_CHOICE,
    INTAKE_FORMAT_CHOICES,
    INCIDENT_DATE_HELPTEXT,
)

from .question_text import (
    CONTACT_QUESTIONS,
    SERVICEMEMBER_QUESTION,
    PRIMARY_REASON_QUESTION,
    HATECRIME_TITLE,
    HATECRIME_QUESTION,
    LOCATION_QUESTIONS,
    ELECTION_QUESTION,
    WORKPLACE_QUESTIONS,
    PUBLIC_QUESTION,
    POLICE_QUESTIONS,
    EDUCATION_QUESTION,
    PROTECTED_CLASS_QUESTION,
    DATE_QUESTIONS,
    SUMMARY_QUESTION,
)

from .phone_regex import phone_validation_regex

import logging

logger = logging.getLogger(__name__)


def _add_empty_choice(choices):
    """Add an empty option to list of choices"""
    return (EMPTY_CHOICE,) + choices


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
            'contact_address_line_1', 'contact_address_line_2', 'contact_state',
            'contact_city', 'contact_zip',
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
            'contact_address_line_1': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.name_id
            }),
            'contact_address_line_2': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.name_id
            }),
            'contact_city': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.name_id
            }),
            'contact_zip': TextInput(attrs={
                'class': 'usa-input',
                'aria-describedby': a11y.name_id
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        a11y = ContactA11y()

        self.label_suffix = ''

        self.fields['contact_first_name'].label = CONTACT_QUESTIONS['contact_first_name']
        self.fields['contact_last_name'].label = CONTACT_QUESTIONS['contact_last_name']
        self.fields['contact_email'].label = CONTACT_QUESTIONS['contact_email']
        self.fields['contact_phone'].label = CONTACT_QUESTIONS['contact_phone']
        self.fields['contact_address_line_1'].label = CONTACT_QUESTIONS['contact_address_line_1']
        self.fields['contact_address_line_2'].label = CONTACT_QUESTIONS['contact_address_line_2']
        self.fields['contact_city'].label = CONTACT_QUESTIONS['contact_city']
        self.fields['contact_zip'].label = CONTACT_QUESTIONS['contact_zip']
        self.fields['contact_state'] = ChoiceField(
            choices=(("", _(' - Select - ')), ) + STATES_AND_TERRITORIES,
            widget=Select(attrs={
                'class': 'usa-select'
            }),
            label=CONTACT_QUESTIONS['contact_state'],
            required=False,
        )
        self.fields['servicemember'] = TypedChoiceField(
            error_messages={'required': SERVICEMEMBER_ERROR},
            widget=UsaRadioSelect(),
            label=SERVICEMEMBER_QUESTION,
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
                ('contact_email', 'contact_phone', 'contact_address_line_1', 'contact_address_line_2'),
                group_name=CONTACT_QUESTIONS['contact_title'],
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
            label=PRIMARY_REASON_QUESTION,
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
            label=HATECRIME_QUESTION,
        )

        self.question_groups = [
            QuestionGroup(
                self,
                ('hatecrimes_trafficking',),
                group_name=HATECRIME_TITLE,
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
        self.fields['violation_summary'].label = SUMMARY_QUESTION
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

        self.fields['location_name'].label = LOCATION_QUESTIONS['location_name']
        self.fields['location_name'].help_text = _('Examples: Name of business, school, intersection, prison, polling place, website, etc.')
        self.fields['location_name'].error_messages = {
            'required': errors['location_name']
        }
        self.fields['location_name'].required = True
        self.fields['location_address_line_1'].label = LOCATION_QUESTIONS['location_address_line_1']
        self.fields['location_address_line_2'].label = LOCATION_QUESTIONS['location_address_line_2']
        self.fields['location_city_town'].label = LOCATION_QUESTIONS['location_city_town']
        self.fields['location_city_town'].error_messages = {
            'required': errors['location_city_town']
        }
        self.fields['location_city_town'].required = True
        self.fields['location_state'] = ChoiceField(
            choices=_add_empty_choice(STATES_AND_TERRITORIES),
            widget=Select(attrs={
                'aria-describedby': 'location-help-text',
                'class': 'usa-select'
            }),
            required=True,
            error_messages={
                'required': errors['location_state']
            },
            label=LOCATION_QUESTIONS['location_state'],
            help_text=_("Where did this happen?"),
        )

        self.question_groups = [
            QuestionGroup(
                self,
                ('location_name', 'location_address_line_1', 'location_address_line_2'),
                group_name=LOCATION_QUESTIONS['location_title'],
                help_text=_('Please be as specific as possible. We will handle this information with sensitivity.'),
                optional=False,
                ally_id='location-help-text'
            ),
        ]


class ElectionLocation(LocationForm):
    class Meta:
        model = Report
        election_fields = ['election_details']
        fields = LocationForm.Meta.fields + election_fields
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)
        self.question_groups = [
            QuestionGroup(
                self,
                ('election_details',),
                group_name=ELECTION_QUESTION,
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
        workplace_fields = [
            'public_or_private_employer',
            'employer_size'
        ]
        fields = LocationForm.Meta.fields + workplace_fields
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)
        self.question_groups = [
            QuestionGroup(
                self,
                ('public_or_private_employer',),
                group_name=WORKPLACE_QUESTIONS['public_or_private_employer'],
                optional=False
            ),
            QuestionGroup(
                self,
                ('employer_size',),
                group_name=WORKPLACE_QUESTIONS['employer_size'],
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
        commercial_fields = ['commercial_or_public_place', 'other_commercial_or_public_place']
        fields = LocationForm.Meta.fields + commercial_fields
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)

        self.name = 'CommericalPublicLocation'

        self.fields['commercial_or_public_place'] = TypedChoiceField(
            label=PUBLIC_QUESTION,
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
        police_fields = ['inside_correctional_facility', 'correctional_facility_type']
        fields = LocationForm.Meta.fields + police_fields
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
            label=POLICE_QUESTIONS['inside_correctional_facility']
        )

        self.fields['correctional_facility_type'] = TypedChoiceField(
            choices=CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
            widget=UsaRadioSelect,
            required=False,
            label=''
        )
        self.fields['correctional_facility_type'].widget.attrs['class'] = 'margin-bottom-0 padding-bottom-0 padding-left-1'
        self.fields['correctional_facility_type'].help_text = POLICE_QUESTIONS['correctional_facility_type']

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
        education_fields = ['public_or_private_school']
        fields = LocationForm.Meta.fields + education_fields
        widgets = LocationForm.Meta.widgets

    def __init__(self, *args, **kwargs):
        LocationForm.__init__(self, *args, **kwargs)

        self.question_groups = [
            QuestionGroup(
                self,
                ('public_or_private_school',),
                group_name=EDUCATION_QUESTION,
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
        widgets = {
            'protected_class': UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'protected-class-help-text'
            }),
            'other_class': TextInput(
                attrs={'class': 'usa-input word-count-10'}
            ),
        }

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
                group_name=PROTECTED_CLASS_QUESTION,
                help_text=_('There are federal and state laws that protect people from discrimination based on their personal characteristics. Here is a list of the most common characteristics that are legally protected. Select any that apply to your incident.'),
                optional=False,
                ally_id="protected-class-help-text"
            )
        ]


def date_cleaner(self, cleaned_data):
    day = cleaned_data.get('last_incident_day') or 1

    if day > 31 or day < 1:
        self.add_error('last_incident_day', ValidationError(
            _('Please enter a valid day of the month. Day must be between 1 and the last day of the month.')
        ))

    try:
        year = cleaned_data['last_incident_year']
        month = cleaned_data['last_incident_month']
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


class When(ModelForm):
    date_question = DATE_QUESTIONS['date_title']
    help_text = INCIDENT_DATE_HELPTEXT

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
                'min': 0
            }),
            'last_incident_year': TextInput(attrs={
                'class': 'usa-input usa-input--medium',
                'required': True,
                'type': 'number',
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['last_incident_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['last_incident_month'].error_messages = {
            'required': _('Please enter a month.'),
        }
        self.fields['last_incident_month'].required = True
        self.fields['last_incident_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['last_incident_year'].label = DATE_QUESTIONS['last_incident_year']
        self.fields['last_incident_year'].error_messages = {
            'required': _('Please enter a year.'),
        }
        self.fields['last_incident_year'].required = True

    def clean(self):
        """Validating more than one field at a time can't be done in the model validation"""
        cleaned_data = super(When, self).clean()
        return date_cleaner(self, cleaned_data)


class Review(ModelForm):
    question_text = {
        'contact': CONTACT_QUESTIONS,
        'servicemember': SERVICEMEMBER_QUESTION,
        'primary_reason': PRIMARY_REASON_QUESTION,
        'hatecrime_title': HATECRIME_TITLE,
        'hatecrime': HATECRIME_QUESTION,
        'location': LOCATION_QUESTIONS,
        'election': ELECTION_QUESTION,
        'workplace': WORKPLACE_QUESTIONS,
        'public': PUBLIC_QUESTION,
        'police': POLICE_QUESTIONS,
        'education': EDUCATION_QUESTION,
        'characteristics': PROTECTED_CLASS_QUESTION,
        'date': DATE_QUESTIONS,
        'summary': SUMMARY_QUESTION,
    }

    class Meta:
        model = Report
        fields = []


class ProForm(
    Contact,
    HateCrimesTrafficking,
    ElectionLocation,
    WorkplaceLocation,
    CommercialPublicLocation,
    PoliceLocation,
    EducationLocation,
    ProtectedClassForm,
    When,
):
    class Meta:
        model = Report

        fields = \
            ['intake_format'] +\
            Contact.Meta.fields +\
            ['primary_complaint'] +\
            HateCrimesTrafficking.Meta.fields +\
            ['location_name', 'location_address_line_1', 'location_address_line_2',
                'location_city_town', 'location_state'] +\
            ElectionLocation.Meta.election_fields +\
            WorkplaceLocation.Meta.workplace_fields +\
            CommercialPublicLocation.Meta.commercial_fields +\
            PoliceLocation.Meta.police_fields +\
            EducationLocation.Meta.education_fields +\
            ProtectedClassForm.Meta.fields +\
            When.Meta.fields +\
            ['crt_reciept_month', 'crt_reciept_day', 'crt_reciept_year'] +\
            ['violation_summary']

        all_widgets = {}

        widget_list = [
            Contact.Meta.widgets,
            HateCrimesTrafficking.Meta.widgets,
            # location widgets
            {
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
            },
            {'other_commercial_or_public_place': TextInput(
                attrs={'class': 'usa-input word-count-10'}
            )},
            When.Meta.widgets,
            {
                'last_incident_month': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'number',
                    'required': False,
                }),
                'last_incident_day': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'number',
                    'min': 0,
                    'required': False,
                }),
                'last_incident_year': TextInput(attrs={
                    'class': 'usa-input usa-input--medium',
                    'type': 'number',
                    'required': False,
                }),
            },
            {
                'crt_reciept_month': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'number',
                    'required': False,
                }),
                'crt_reciept_day': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'number',
                    'min': 0,
                    'required': False,
                }),
                'crt_reciept_year': TextInput(attrs={
                    'class': 'usa-input usa-input--medium',
                    'type': 'number',
                    'required': False,
                }),
            },
        ]
        for widget in widget_list:
            all_widgets.update(widget)
        widgets = all_widgets

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        Contact.__init__(self, *args, **kwargs)
        self.fields['intake_format'] = TypedChoiceField(
            choices=(
                EMPTY_CHOICE,
                ('letter', 'letter'),
                ('phone', 'phone'),
                ('fax', 'fax'),
            ),
            widget=Select(attrs={
                'class': 'usa-select',
            }),
            required=False,
        )
        self.fields['servicemember'] = TypedChoiceField(
            choices=SERVICEMEMBER_CHOICES,
            label=SERVICEMEMBER_QUESTION,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        self.fields['primary_complaint'] = TypedChoiceField(
            choices=PRIMARY_COMPLAINT_CHOICES,
            error_messages={'required': PRIMARY_COMPLAINT_ERROR},
            label=PRIMARY_REASON_QUESTION,
            widget=UsaRadioSelect,
            required=True,
        )
        # hate crimes
        self.fields['public_or_private_employer'] = TypedChoiceField(
            choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        self.fields['employer_size'] = TypedChoiceField(
            choices=EMPLOYER_SIZE_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        self.fields['public_or_private_school'] = TypedChoiceField(
            choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        self.fields['election_details'] = TypedChoiceField(
            choices=ELECTION_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        self.fields['inside_correctional_facility'] = TypedChoiceField(
            choices=CORRECTIONAL_FACILITY_LOCATION_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        self.fields['correctional_facility_type'] = TypedChoiceField(
            choices=CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
            widget=UsaRadioSelect,
            required=False,
            label=POLICE_QUESTIONS['correctional_facility_type']
        )
        self.fields['commercial_or_public_place'] = TypedChoiceField(
            choices=COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        # incident location
        self.fields['protected_class'] = ModelMultipleChoiceField(
            error_messages={'required': PROTECTED_CLASS_ERROR},
            required=False,
            label=PROTECTED_CLASS_QUESTION,
            queryset=ProtectedClass.objects.filter(protected_class__in=PROTECTED_CLASS_CHOICES).order_by('form_order'),
            widget=UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'protected-class-help-text'
            }),
        )
        self.fields['last_incident_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['last_incident_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['last_incident_year'].label = DATE_QUESTIONS['last_incident_year']

        self.fields['crt_reciept_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['crt_reciept_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['crt_reciept_year'].label = DATE_QUESTIONS['last_incident_year']

        self.fields['violation_summary'].widget.attrs['class'] = 'usa-textarea word-count-500'
        self.label_suffix = ''
        self.fields['violation_summary'].label = SUMMARY_QUESTION
        self.fields['violation_summary'].widget.attrs['aria-describedby'] = 'details-help-text'

    def clean(self):
        """Validating more than one field at a time can't be done in the model validation"""
        cleaned_data = super(ProForm, self).clean()
        if cleaned_data['last_incident_year'] is not None and cleaned_data['last_incident_month'] is not None:
            return date_cleaner(self, cleaned_data)
        else:
            return cleaned_data


class Filters(ModelForm):
    status = ChoiceField(
        choices=_add_empty_choice(STATUS_CHOICES),
        widget=Select(attrs={
            'name': 'status',
            'class': 'usa-select',
        })
    )
    location_state = ChoiceField(
        choices=_add_empty_choice(STATES_AND_TERRITORIES),
        widget=Select(attrs={
            'name': 'location_state',
            'class': 'usa-select',
        })
    )

    class Meta:
        model = Report
        fields = [
            'assigned_section',
            'contact_first_name',
            'contact_last_name',
            'location_city_town',
            'location_state',
            'status',
        ]

        labels = {
            'assigned_section': _('View sections'),
            'contact_first_name': _('Contact first name'),
            'contact_last_name': _('Contact last name'),
            'location_city_town': _('Incident location city'),
            'location_state': _('Incident location state')
        }

        widgets = {
            'assigned_section': CrtMultiSelect(attrs={
                'classes': 'text-uppercase',
                'name': 'assigned_section'
            }),
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
            })
        }


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

    def get_actions(self):
        """Parse incoming changed data for activity stream entry"""
        for field in self.changed_data:
            yield f"updated {' '.join(field.split('_'))}", f" with value {self.cleaned_data[field]}"

    def update_activity_stream(self, user):
        """Send all actions to activity stream"""
        from actstream import action
        for verb, description in self.get_actions():
            action.send(
                user,
                verb=verb,
                description=description,
                target=self.instance
            )
