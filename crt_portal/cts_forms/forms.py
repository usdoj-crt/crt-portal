import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.utils.functional import cached_property

from django.forms import (BooleanField, CharField, CheckboxInput, ChoiceField,
                          EmailInput, ModelChoiceField, ModelForm,
                          ModelMultipleChoiceField, Select, SelectMultiple,
                          Textarea, TextInput, TypedChoiceField)
from django.utils.translation import gettext_lazy as _

from .model_variables import (COMMERCIAL_OR_PUBLIC_ERROR,
                              COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
                              COMMERCIAL_OR_PUBLIC_PLACE_HELP_TEXT,
                              CORRECTIONAL_FACILITY_LOCATION_CHOICES,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
                              DATE_ERRORS, DISTRICT_CHOICES, ELECTION_CHOICES,
                              EMPLOYER_SIZE_CHOICES, EMPLOYER_SIZE_ERROR,
                              EMPTY_CHOICE, INCIDENT_DATE_HELPTEXT,
                              POLICE_LOCATION_ERRORS,
                              PRIMARY_COMPLAINT_CHOICES,
                              PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
                              PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
                              PRIMARY_COMPLAINT_ERROR, PROTECTED_CLASS_ERROR,
                              PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
                              PUBLIC_OR_PRIVATE_EMPLOYER_ERROR,
                              PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
                              SECTION_CHOICES, SERVICEMEMBER_CHOICES,
                              SERVICEMEMBER_ERROR, STATES_AND_TERRITORIES,
                              STATUS_CHOICES, STATUTE_CHOICES,
                              VIOLATION_SUMMARY_ERROR, VOTING_ERROR,
                              WHERE_ERRORS)
from .models import (CommentAndSummary, HateCrimesandTrafficking,
                     ProtectedClass, Report)
from .phone_regex import phone_validation_regex
from .question_group import QuestionGroup
from .question_text import (CONTACT_QUESTIONS, DATE_QUESTIONS,
                            EDUCATION_QUESTION, ELECTION_QUESTION,
                            HATECRIME_QUESTION, HATECRIME_TITLE,
                            LOCATION_QUESTIONS, POLICE_QUESTIONS,
                            PRIMARY_REASON_QUESTION, PROTECTED_CLASS_QUESTION,
                            PUBLIC_QUESTION, SERVICEMEMBER_QUESTION,
                            SUMMARY_HELPTEXT, SUMMARY_QUESTION,
                            WORKPLACE_QUESTIONS)
from .widgets import (ComplaintSelect, CrtMultiSelect,
                      CrtPrimaryIssueRadioGroup, UsaCheckboxSelectMultiple,
                      UsaRadioSelect)

logger = logging.getLogger(__name__)
User = get_user_model()


def _add_empty_choice(choices):
    """Add an empty option to list of choices"""
    if isinstance(choices, list):
        choices = tuple(choices)
    return (EMPTY_CHOICE,) + choices


class ActivityStreamUpdater(object):
    """Utility functions to update activity stream for all changed fields"""

    def get_actions(self):
        """Parse incoming changed data for activity stream entry"""
        for field in self.changed_data:
            try:
                initial = self.initial[field]
                new = self.cleaned_data[field]
                if isinstance(initial, list):
                    initial = ', '.join([str(x) for x in initial])
                    new = ', '.join([str(x) for x in new])

                yield f"{' '.join(field.split('_')).capitalize()}:", f'Updated from "{initial}" to "{new}"'
            except KeyError:
                # Initial value not found for field, not present on model, not a change to be tracked
                pass

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


class Contact(ModelForm):
    class Meta:
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
            }),
            'contact_last_name': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_email': EmailInput(attrs={
                'class': 'usa-input',
            }),
            'contact_phone': TextInput(attrs={
                'class': 'usa-input',
                'pattern': phone_validation_regex,
                'title': _('If you submit a phone number, please make sure to include between 7 and 15 digits. The characters "+", ")", "(", "-", and "." are allowed. Please include country code if entering an international phone number.')
            }),
            'contact_address_line_1': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_address_line_2': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_city': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_zip': TextInput(attrs={
                'class': 'usa-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
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
            # Translators: this is the default- blank options for a drop-down menu where a user chooses a state
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
            # Translators: This is help text for the question asking if someone is a service member
            help_text=_('If you’re reporting on behalf of someone else, please select their status.'),
            empty_value=None,
            choices=SERVICEMEMBER_CHOICES,
        )
        self.question_groups = [
            QuestionGroup(
                self,
                ('contact_first_name', 'contact_last_name'),
                group_name=CONTACT_QUESTIONS['contact_name_title'],
            ),
            QuestionGroup(
                self,
                ('contact_email', 'contact_phone', 'contact_address_line_1', 'contact_address_line_2'),
                group_name=CONTACT_QUESTIONS['contact_title'],
            )
        ]
        self.help_text = CONTACT_QUESTIONS['contact_help_text'],
        self.lede_text = _('If you believe you or someone else has experienced a civil rights violation, please tell us what happened.')


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
            queryset=HateCrimesandTrafficking.objects.all(),
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
                optional=True,
                label_cls="margin-bottom-4",
                help_cls="text-bold",
                ally_id="hatecrimes-help-text"
            )
        ]
        # Translators: notes that this page is the same form step as the page before
        self.page_note = _('Continued')


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
        self.fields['violation_summary'].help_text = SUMMARY_HELPTEXT
        self.fields['violation_summary'].error_messages = {'required': VIOLATION_SUMMARY_ERROR}
        self.fields['violation_summary'].required = True
        self.page_note = _('Continued')


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
                optional=False,
                ally_id='location-help-text'
            ),
        ]
        self.page_note = _('Please tell us the city, state, and name of the location where this incident took place. This ensures your concern is reviewed by the right people within the Civil Rights Division.')


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
                'required': VOTING_ERROR
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
                    'public_employer': _('Public employers include organizations funded by the government like the military, post office, fire department, courthouse, DMV, or public school. This could be at the local or state level.'),
                    'private_employer': _('Private employers are business or non-profits not funded by the government such as retail stores, banks, or restaurants.')
                }
            }),
            required=True,
            error_messages={
                'required': PUBLIC_OR_PRIVATE_EMPLOYER_ERROR
            },
            label=''
        )

        self.fields['employer_size'] = TypedChoiceField(
            choices=EMPLOYER_SIZE_CHOICES,
            widget=UsaRadioSelect,
            required=True,
            error_messages={
                'required': EMPLOYER_SIZE_ERROR
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
                'required': COMMERCIAL_OR_PUBLIC_ERROR
            }
        )
        # Translators: describe the "other" option for commercial or public place question
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
            queryset=ProtectedClass.active_choices.all().order_by('form_order'),
            widget=UsaCheckboxSelectMultiple(attrs={
                'aria-describedby': 'protected-class-help-text'
            }),
        )
        # Translators: This is to explain an "other" choice for personal characteristics
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
    """This should give the most specific error message, if the date doesn't render for reasons other than what we are checking for, it will give the generic error."""
    try:
        # If these are required they will be caught by the key error
        day = cleaned_data.get('last_incident_day') or 1
        year = cleaned_data['last_incident_year']
        month = cleaned_data['last_incident_month']
        # custom messages
        if day > 31 or day < 1:
            self.add_error('last_incident_day', ValidationError(
                DATE_ERRORS['day_invalid'],
            ))
        elif datetime(year, month, day) > datetime.now():
            self.add_error('last_incident_year', ValidationError(
                DATE_ERRORS['no_future'],
                params={'value': datetime(year, month, day).strftime('%x')},
            ))
        elif datetime(year, month, day) < datetime(1899, 12, 31):
            self.add_error('last_incident_year', ValidationError(
                DATE_ERRORS['no_past'],
                params={'value': datetime(year, month, day).strftime('%x')},
            ))

    except ValueError:
        # a bit of a catch-all for all the ways people could make invalid dates
        self.add_error('last_incident_year', ValidationError(
            DATE_ERRORS['not_valid'],
            params={'value': f'{month}/{day}/{year}'},
        ))
    except KeyError:
        # these required errors will be caught by the built in error validation
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
                'label': DATE_QUESTIONS['last_incident_month']
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
            'required': DATE_ERRORS['month_required'],
        }
        self.fields['last_incident_month'].required = True
        self.fields['last_incident_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['last_incident_year'].label = DATE_QUESTIONS['last_incident_year']
        self.fields['last_incident_year'].error_messages = {
            'required': DATE_ERRORS['year_required'],
        }
        self.fields['last_incident_year'].required = True
        self.page_note = _('It is important for us to know how recently this incident happened so we can take the appropriate action. If this happened over a period of time or is still happening, please provide the most recent date.')

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
    """This form is for CRT only for complaints that come from other sources than the public web form"""
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
            {'other_class': TextInput(attrs={
                'class': 'usa-input',
            })},
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
                attrs={'class': 'usa-input'}
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
                ('email', 'email'),
            ),
            widget=Select(attrs={
                'class': 'usa-select mobile-lg:grid-col-7',
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
            queryset=ProtectedClass.active_choices.all().order_by('form_order'),
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

        if 'violation_summary' in self.fields:
            self.fields['violation_summary'].widget.attrs['class'] = 'usa-textarea word-count-500'
            self.label_suffix = ''
            self.fields['violation_summary'].label = SUMMARY_QUESTION
            self.fields['violation_summary'].widget.attrs['aria-describedby'] = 'details-help-text'
            self.fields['violation_summary'].help_text = _('What did the person believe happened?')

    def clean(self):
        """Validating more than one field at a time can't be done in the model validation"""
        cleaned_data = super(ProForm, self).clean()
        if cleaned_data['last_incident_year'] and cleaned_data['last_incident_month']:
            return date_cleaner(self, cleaned_data)
        else:
            return cleaned_data


class Filters(ModelForm):
    status = ChoiceField(
        required=False,
        choices=_add_empty_choice(STATUS_CHOICES),
        widget=Select(attrs={
            'name': 'status',
            'class': 'usa-select',
        })
    )
    location_state = ChoiceField(
        required=False,
        choices=_add_empty_choice(STATES_AND_TERRITORIES),
        widget=Select(attrs={
            'name': 'location_state',
            'class': 'usa-select'
        })
    )
    primary_statute = ChoiceField(
        required=False,
        choices=_add_empty_choice(STATUTE_CHOICES),
        widget=Select(attrs={
            'name': 'primary_statute',
            'class': 'usa-select'
        })
    )
    summary = CharField(
        required=False,
        widget=TextInput(
            attrs={
                'class': 'usa-input',
                'name': 'summary',
            },
        ),
    )
    assigned_to = ModelChoiceField(
        required=False,
        queryset=User.objects.filter(is_active=True),
        label=_("Assigned to"),
        to_field_name='username',
        widget=Select(attrs={
            'name': 'assigned_to',
            'class': 'usa-input'
        })
    )

    class Meta:
        model = Report
        fields = [
            'assigned_section',
            'contact_first_name',
            'contact_last_name',
            'location_city_town',
            'location_name',
            'location_state',
            'status',
            'assigned_to',
            'public_id',
            'primary_statute',
            'violation_summary',
        ]

        labels = {
            # Translators: CRT sections
            'assigned_section': _('View sections'),
            'contact_first_name': _('Contact first name'),
            'contact_last_name': _('Contact last name'),
            'location_city_town': _('Incident location city'),
            'location_name': _('Incident location name'),
            'location_state': _('Incident location state'),
            'assigned_to': _('Assignee'),
            'public_id': _('Complaint ID'),
            'primary_statute': _('Statute'),
            'violation_summary': _('Personal description'),
        }

        widgets = {
            'assigned_section': CrtMultiSelect(attrs={
                'class': 'text-uppercase',
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
            }),
            'location_name': TextInput(attrs={
                'class': 'usa-input',
                'name': 'location_name'
            }),
            'public_id': TextInput(attrs={
                'class': 'usa-input',
                'name': 'public_id'
            }),
            'violation_summary': TextInput(attrs={
                'class': 'usa-input',
                'name': 'violation_summary'
            }),
        }


class ComplaintActions(ModelForm, ActivityStreamUpdater):
    CONTEXT_KEY = 'actions'
    assigned_to = ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label=_("Assigned to"),
        required=False
    )

    class Meta:
        model = Report
        fields = ['assigned_section', 'status', 'primary_statute', 'district', 'assigned_to']

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['assigned_section'] = ChoiceField(
            widget=ComplaintSelect(
                label='Section',
                attrs={'class': 'usa-select text-bold text-uppercase crt-dropdown__data'},
            ),
            choices=SECTION_CHOICES,
            required=False
        )
        self.fields['status'] = ChoiceField(
            widget=ComplaintSelect(
                label='Status',
                attrs={
                    'class': 'crt-dropdown__data',
                },

            ),
            choices=STATUS_CHOICES,
            required=False
        )
        self.fields['primary_statute'] = ChoiceField(
            widget=ComplaintSelect(
                label='Primary statute',
                attrs={
                    'class': 'text-uppercase crt-dropdown__data',
                },
            ),
            choices=_add_empty_choice(STATUTE_CHOICES),
            required=False
        )
        self.fields['district'] = ChoiceField(
            widget=ComplaintSelect(
                label='Judicial district',
                attrs={
                    'class': 'text-uppercase crt-dropdown__data',
                },
            ),
            choices=_add_empty_choice(DISTRICT_CHOICES),
            required=False
        )
        self.fields['assigned_to'].widget.label = 'Assigned to'

    def get_actions(self):
        """Parse incoming changed data for activity stream entry"""
        for field in self.changed_data:
            yield f"{' '.join(field.split('_')).capitalize()}:", f'Updated from "{self.initial[field]}" to "{self.cleaned_data[field]}"'

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

    def success_message(self):
        """Prepare update success message for rendering in template"""
        updated_fields = [self.fields[field].widget.label for field in self.changed_data]
        if len(updated_fields) == 1:
            message = f"Successfully updated {updated_fields[0]}."
        else:
            fields = ', '.join(updated_fields[:-1])
            fields += f', and {updated_fields[-1]}'
            message = f"Successfully updated {fields}."
        return message


class CommentActions(ModelForm):
    class Meta:
        model = CommentAndSummary
        fields = ['note', 'is_summary']

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['note'].widget = Textarea(
            attrs={
                'class': 'usa-textarea',
                'id': 'id_note-comment',
            },
        )
        self.fields['note'].label = 'New comment'
        self.fields['is_summary'] = CharField()

    def update_activity_stream(self, user, report, verb):
        """Send all actions to activity stream"""
        from actstream import action
        action.send(
            user,
            verb=verb,
            description=self.instance.note,
            target=report
        )


class SummaryField(CommentActions):
    """Need to override the html id since it is on the same page as the comment form"""
    def __init__(self, *args, **kwargs):
        CommentActions.__init__(self, *args, **kwargs)
        self.fields['note'].widget = Textarea(
            attrs={
                'class': 'usa-textarea',
                'id': 'id_note-summary',
            },
        )


class ContactEditForm(ModelForm, ActivityStreamUpdater):
    CONTEXT_KEY = 'contact_form'
    SUCCESS_MESSAGE = "Successfully updated contact information."
    FAIL_MESSAGE = "Failed to update contact details."

    contact_state = ChoiceField(
        choices=(("", _(' - Select - ')), ) + STATES_AND_TERRITORIES,
        widget=Select(attrs={
            'class': 'usa-input usa-select'
        }),
        label=CONTACT_QUESTIONS['contact_state'],
        required=False,
    )

    class Meta:
        model = Report
        fields = [
            'contact_first_name', 'contact_last_name',
            'contact_email', 'contact_phone', 'contact_address_line_1',
            'contact_address_line_2', 'contact_state',
            'contact_city', 'contact_zip',
        ]

        widgets = {
            'contact_first_name': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_last_name': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_email': EmailInput(attrs={
                'class': 'usa-input',
            }),
            'contact_phone': TextInput(attrs={
                'class': 'usa-input',
                'pattern': phone_validation_regex,
                'title': _('If you submit a phone number, please make sure to include between 7 and 15 digits. The characters "+", ")", "(", "-", and "." are allowed. Please include country code if entering an international phone number.')
            }),
            'contact_address_line_1': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_address_line_2': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_city': TextInput(attrs={
                'class': 'usa-input',
            }),
            'contact_zip': TextInput(attrs={
                'class': 'usa-input',
            }),
        }

    def success_message(self):
        return self.SUCCESS_MESSAGE


class ReportEditForm(ProForm, ActivityStreamUpdater):
    CONTEXT_KEY = "details_form"
    FAIL_MESSAGE = "Failed to update complaint details."
    SUCCESS_MESSAGE = "Successfully updated complaint details."

    hatecrime = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'usa-checkbox__input'}))
    trafficking = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'usa-checkbox__input'}))

    class Meta(ProForm.Meta):
        exclude = ['intake_format', 'violation_summary', 'contact_first_name', 'contact_last_name',
                   'contact_email', 'contact_phone', 'contact_address_line_1', 'contact_address_line_2', 'contact_state',
                   'contact_city', 'contact_zip']

    def success_message(self):
        return self.SUCCESS_MESSAGE

    def _set_to_select_widget(self, field):
        """Set the provided 'field's widget to Select and add an empty choice"""
        self.fields[field] = TypedChoiceField(
            choices=_add_empty_choice(self.fields[field].choices),
            widget=Select(attrs={'class': 'usa-select'}),
            required=False,
        )

    def __init__(self, *args, **kwargs):
        # Don't need all of the __init__ from ProForm
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['hatecrime'].initial = self.instance.hatecrimes_trafficking.filter(value='physical_harm').exists()
        self.fields['trafficking'].initial = self.instance.hatecrimes_trafficking.filter(value='trafficking').exists()

        # required fields
        self.fields['primary_complaint'].widget = Select(choices=self.fields['primary_complaint'].choices, attrs={'class': 'usa-select'})
        self.fields['protected_class'].widget = SelectMultiple(choices=self.fields['protected_class'].choices, attrs={'class': 'height-10 width-mobile'})
        self.fields['servicemember'].widget = Select(choices=self.fields['servicemember'].choices, attrs={'class': 'usa-select'})

        # primary_complaint dependents, optional
        self._set_to_select_widget('public_or_private_school')
        self._set_to_select_widget('public_or_private_employer')
        self._set_to_select_widget('employer_size')
        self._set_to_select_widget('election_details')
        self._set_to_select_widget('inside_correctional_facility')
        self._set_to_select_widget('correctional_facility_type')
        self._set_to_select_widget('commercial_or_public_place')

        # date field labels
        self.fields['last_incident_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['last_incident_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['last_incident_year'].label = DATE_QUESTIONS['last_incident_year']

    @cached_property
    def changed_data(self):
        changed_data = super().changed_data
        # If hatecrime or trafficking field was changed, so was hatecrimes_trafficking
        if set(changed_data).intersection({'hatecrime', 'trafficking'}) and 'hatecrimes_trafficking' not in changed_data:
            changed_data.append('hatecrimes_trafficking')

        # If we're changing primary complaint, we may also need to update dependent fields
        if 'primary_complaint' in changed_data:
            original = self.instance.primary_complaint
            if original in Report.PRIMARY_COMPLAINT_DEPENDENT_FIELDS.keys():
                for field in Report.PRIMARY_COMPLAINT_DEPENDENT_FIELDS[original]:
                    # If there's an initial value, we're setting it to None
                    # in the last step of processing, self.clean()
                    # Add to changed_data here so the instance is aware of
                    # the modification
                    if self[field].initial:
                        changed_data.append(field)

        return changed_data

    def clean_dependent_fields(self, cleaned_data):
        """
        If primary complaint is changed, set any dependent fields associated with initial value to None
        """
        if 'primary_complaint' in self.changed_data:
            original = self.instance.primary_complaint
            if original in Report.PRIMARY_COMPLAINT_DEPENDENT_FIELDS.keys():
                for field in Report.PRIMARY_COMPLAINT_DEPENDENT_FIELDS[original]:
                    cleaned_data[field] = ""
        return cleaned_data

    def clean(self):
        """Convert intermediary fields rendered as checkboxes to model's M2M field"""
        cleaned_data = super().clean()
        crimes = []
        if cleaned_data['hatecrime']:
            crimes.append(HateCrimesandTrafficking.objects.get(value='physical_harm'))
        if cleaned_data['trafficking']:
            crimes.append(HateCrimesandTrafficking.objects.get(value='trafficking'))
        cleaned_data['hatecrimes_trafficking'] = crimes

        cleaned_data = self.clean_dependent_fields(cleaned_data)
        return cleaned_data


