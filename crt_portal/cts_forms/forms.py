import logging
from datetime import datetime, timezone
from actstream import action

from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.forms import (BooleanField, CharField, CheckboxInput, ChoiceField,
                          ClearableFileInput, DateField,
                          EmailInput, HiddenInput, IntegerField,
                          ModelChoiceField, ModelForm, Form,
                          ModelMultipleChoiceField, MultipleChoiceField,
                          Select, SelectMultiple, Textarea, TextInput,
                          TypedChoiceField)
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .model_variables import (COMMERCIAL_OR_PUBLIC_ERROR,
                              COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
                              COMMERCIAL_OR_PUBLIC_PLACE_HELP_TEXT,
                              CONTACT_PHONE_INVALID_MESSAGE,
                              CORRECTIONAL_FACILITY_LOCATION_CHOICES,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
                              DATE_ERRORS, DISTRICT_CHOICES,
                              EMPLOYER_SIZE_CHOICES, EMPLOYER_SIZE_ERROR,
                              INCIDENT_DATE_HELPTEXT,
                              INTAKE_FORMAT_CHOICES,
                              INTAKE_FORMAT_ERROR,
                              POLICE_LOCATION_ERRORS, PER_PAGE,
                              PRIMARY_COMPLAINT_CHOICES,
                              PRIMARY_COMPLAINT_CHOICES_VOTING,
                              PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES,
                              PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES_VOTING,
                              PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
                              PRIMARY_COMPLAINT_ERROR,
                              PRIMARY_COMPLAINT_PROFORM_CHOICES,
                              PRIMARY_COMPLAINT_PROFORM_CHOICES_VOTING,
                              PRINT_CHOICES,
                              PROTECTED_CLASS_ERROR,
                              PROTECTED_MODEL_CHOICES,
                              PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
                              PUBLIC_OR_PRIVATE_EMPLOYER_ERROR,
                              PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
                              SECTION_CHOICES_WITHOUT_LABELS,
                              SERVICEMEMBER_CHOICES,
                              SERVICEMEMBER_ERROR, STATES_AND_TERRITORIES,
                              STATUS_CHOICES, STATUTE_CHOICES,
                              VIOLATION_SUMMARY_ERROR, WHERE_ERRORS,
                              HATE_CRIME_CHOICES, GROUPING)
from .models import (CommentAndSummary,
                     ProtectedClass, Report, ResponseTemplate, Profile, ReportAttachment, Campaign)
from .phone_regex import phone_validation_regex
from .question_group import QuestionGroup
from .question_text import (CONTACT_QUESTIONS, DATE_QUESTIONS,
                            EDUCATION_QUESTION, ELECTION_QUESTION,
                            LOCATION_QUESTIONS, POLICE_QUESTIONS,
                            PRIMARY_REASON_QUESTION, PROTECTED_CLASS_QUESTION,
                            PUBLIC_QUESTION, SERVICEMEMBER_QUESTION,
                            SUMMARY_HELPTEXT, SUMMARY_QUESTION,
                            WORKPLACE_QUESTIONS, HATE_CRIME_HELP_TEXT,
                            HATE_CRIME_QUESTION)
from .widgets import (ComplaintSelect, CrtMultiSelect,
                      CrtPrimaryIssueRadioGroup, DjNumberWidget, UsaCheckboxSelectMultiple,
                      UsaRadioSelect, DataAttributesSelect, CrtDateInput, add_empty_choice)
from utils.voting_mode import is_voting_mode


logger = logging.getLogger(__name__)
User = get_user_model()


def add_activity(user, verb, description, instance):
    action.send(
        user,
        verb=verb,
        description=description,
        target=instance
    )


class ActivityStreamUpdater(object):
    """Utility functions to update activity stream for all changed fields"""

    def get_actions(self):
        """Parse incoming changed data for activity stream entry"""
        for field in self.changed_data:
            try:
                # TODO? Add display values to activity stream
                initial = self.initial[field]
                new = self.cleaned_data[field]
                if isinstance(initial, list):
                    initial = ', '.join([str(x) for x in initial])
                    new = ', '.join([str(x) for x in new])

                # CRT views only
                yield f"{' '.join(field.split('_')).capitalize()}:", f'Updated from "{initial}" to "{new}"'
            except KeyError:
                # Initial value not found for field, not present on model, not a change to be tracked
                pass

    def update_activity_stream(self, user):
        """Send all actions to activity stream"""
        for verb, description in self.get_actions():
            add_activity(user, verb, description, self.instance)


def save_form(form_data_dict, **kwargs):
    """Saving all the report form data, in use for the public form and the Pro form
    """
    m2m_protected_class = form_data_dict.pop('protected_class')
    r = Report.objects.create(**form_data_dict)

    # Many to many fields need to be added or updated to the main model, with a related manager such as add() or update()
    for protected in m2m_protected_class:
        r.protected_class.add(protected)

    r.assigned_section = r.assign_section()
    r.district = r.assign_district()
    if kwargs.get('intake_format'):
        r.intake_format = kwargs.get('intake_format')
    r.save()
    # adding this back for the save page results
    form_data_dict['protected_class'] = m2m_protected_class.values()
    return form_data_dict, r


ORIGINATION_FIELDS = [
    'origination_utm_source',
    'origination_utm_medium',
    'origination_utm_campaign',
    'unknown_origination_utm_campaign',
    'origination_utm_term',
    'origination_utm_content',
]


class Contact(ModelForm):
    class Meta:
        model = Report
        fields = [
            'contact_first_name', 'contact_last_name',
            'contact_email', 'contact_phone', 'servicemember',
            'contact_address_line_1', 'contact_address_line_2', 'contact_state',
            'contact_city', 'contact_zip', *ORIGINATION_FIELDS
        ]
        widgets = {
            **{
                field: HiddenInput()
                for field in ORIGINATION_FIELDS
            },
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
                'title': CONTACT_PHONE_INVALID_MESSAGE
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
        self.fields['contact_phone'].error_messages = {'invalid': CONTACT_PHONE_INVALID_MESSAGE}

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
        complaint_choices = PRIMARY_COMPLAINT_CHOICES_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_CHOICES
        complaint_choices_examples = PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_CHOICES_TO_EXAMPLES
        self.fields['primary_complaint'] = ChoiceField(
            choices=complaint_choices,
            widget=CrtPrimaryIssueRadioGroup(attrs={
                'choices_to_examples': complaint_choices_examples,
                'choices_to_helptext': PRIMARY_COMPLAINT_CHOICES_TO_HELPTEXT,
            }),
            required=True,
            error_messages={
                'required': PRIMARY_COMPLAINT_ERROR
            },
            label=PRIMARY_REASON_QUESTION,
            help_text=_('Select the reason that best describes your concern. Each reason lists examples of civil rights violations that may relate to your incident. In another section of this report, you will be able to describe your concern in your own words.'),
        )


class Details(ModelForm):
    class Meta:
        model = Report
        fields = [
            'violation_summary',
            'language'
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
                'class': 'usa-input'
            }),
            'location_address_line_1': TextInput(attrs={
                'class': 'usa-input'
            }),
            'location_address_line_2': TextInput(attrs={
                'class': 'usa-input'
            }),
            'location_city_town': TextInput(attrs={
                'class': 'usa-input'
            }),
            'location_state': Select(attrs={
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
            choices=add_empty_choice(STATES_AND_TERRITORIES),
            widget=Select(attrs={
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
                optional=True,  # a11y: only some fields here are required
                extra_validation_fields=('location_city_town', 'location_state')
            ),
        ]
        self.page_note = _('Please tell us the city, state, and name of the location where this incident took place. This ensures your report is reviewed by the right people within the Civil Rights Division.')

    def summary_error_questions(self):
        """
        Return a list of questions which contain fields with errors

        First check all defined question groups
        Then check any fields defined outside of questions groups
        that have not already been evaluated as part of a question group
        """
        questions = []
        checked_fields = set()

        for group in self.question_groups:
            if group.errors():
                questions.append(group.group_name)
            [checked_fields.add(field) for field in group.fields]
            if group.extra_validation_fields:
                [checked_fields.add(field) for field in group.extra_validation_fields]

        for field in self.fields:
            if field not in checked_fields and self[field].errors:
                questions.append(self[field].label)
                checked_fields.add(field)

        return questions


class ElectionLocation(LocationForm):
    pass


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
            label=POLICE_QUESTIONS['correctional_facility_type']
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
            ),
        ] + self.question_groups

        self.fields['public_or_private_school'] = TypedChoiceField(
            choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
            widget=UsaRadioSelect(),
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
            'protected_class': UsaCheckboxSelectMultiple(),
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
            label=PROTECTED_CLASS_QUESTION,
            help_text=_('There are federal and state laws that protect people from discrimination based on their personal characteristics. Here is a list of the most common characteristics that are legally protected. Select any that apply to your incident.'),
            queryset=ProtectedClass.active_choices.all().order_by('form_order'),
            widget=UsaCheckboxSelectMultiple(),
        )
        # Translators: This is to explain an "other" choice for personal characteristics
        self.fields['other_class'].help_text = _('Please describe "Other reason"')
        self.fields['other_class'].widget = TextInput(
            attrs={'class': 'usa-input word-count-10'}
        )


def date_cleaner(self, cleaned_data):
    """This should give the most specific error message, if the date doesn't render for reasons other than what we are checking for, it will give the generic error."""
    try:
        # If these are required they will be caught by the key error
        day = cleaned_data.get('last_incident_day') or 1
        year = cleaned_data['last_incident_year']
        month = cleaned_data['last_incident_month']
        # custom messages
        if month > 12 or month < 1:
            self.add_error('last_incident_month', ValidationError(
                DATE_ERRORS['month_invalid'],
            ))
        elif day > 31 or day < 1:
            self.add_error('last_incident_day', ValidationError(
                DATE_ERRORS['day_invalid'],
            ))
        elif datetime(year, month, day) > datetime.now():
            self.add_error('last_incident_year', ValidationError(
                DATE_ERRORS['no_future'],
                params={'value': datetime(year, month, day).strftime('%x')},
            ))
        elif datetime(year, month, day) < datetime(1900, 1, 1):
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


def crt_date_cleaner(self, cleaned_data):
    """This should give the most specific error message, if the date doesn't render for reasons other than what we are checking for, it will give the generic error."""
    invalid_date = False
    # Test Receipt Month
    if 'crt_reciept_month' in cleaned_data:
        month = cleaned_data['crt_reciept_month']
        # These checks are to prevent existing report detail page edits to require the crt_. . . fields.  They are required in the pro form and that is caught through the existing "required" validation.
        if type(month) != int:
            return cleaned_data
        elif month > 12 or month < 1:
            self.add_error('crt_reciept_month', ValidationError(
                DATE_ERRORS['month_invalid'],
            ))
            invalid_date = True
    else:
        self.add_error('crt_reciept_month', ValidationError(DATE_ERRORS['month_required']))
        invalid_date = True
    # Test Receipt Day
    if 'crt_reciept_day' in cleaned_data:
        day = cleaned_data['crt_reciept_day']
        if type(day) != int:
            return cleaned_data
        elif day > 31 or day < 1:
            self.add_error('crt_reciept_day', ValidationError(
                DATE_ERRORS['day_invalid'],
            ))
            invalid_date = True
    else:
        self.add_error('crt_reciept_day', ValidationError(DATE_ERRORS['day_required']))
        invalid_date = True
    # Test Receipt Year
    if 'crt_reciept_year' in cleaned_data:
        year = cleaned_data['crt_reciept_year']
        if type(year) != int:
            return cleaned_data
        elif year < 2000:
            self.add_error('crt_reciept_year', ValidationError(
                DATE_ERRORS['crt_no_past'],
            ))
        elif invalid_date:
            # Added if month and year are invalid.  We don't want to create a datetime with bad data, which happens in the next conditional.
            return cleaned_data
    else:
        self.add_error('crt_reciept_year', ValidationError(DATE_ERRORS['year_required']))
    if 'crt_reciept_year' in cleaned_data and 'crt_reciept_month' in cleaned_data and 'crt_reciept_day' in cleaned_data:
        try:
            if datetime(year, month, day) > datetime.now():
                self.add_error('crt_reciept_year', ValidationError(
                    DATE_ERRORS['no_future'],
                    params={'value': datetime(year, month, day).strftime('%x')},
                ))
        except ValueError:
            self.add_error('crt_reciept_year', ValidationError(
                DATE_ERRORS['crt_not_valid'],
            ))
    if 'last_incident_day' in cleaned_data:
        incident_day = cleaned_data['last_incident_day']
        if type(incident_day) != int:
            return cleaned_data
        elif incident_day > 31 or incident_day < 1:
            self.add_error('last_incident_day', ValidationError(
                DATE_ERRORS['day_invalid'],
            ))
        if 'last_incident_month' in cleaned_data:
            incident_month = cleaned_data['last_incident_month']
            if type(incident_month) != int:
                return cleaned_data
            elif incident_month > 12 or incident_month < 1:
                self.add_error('last_incident_month', ValidationError(
                    DATE_ERRORS['month_invalid'],
                ))
    if 'last_incident_year' in cleaned_data:
        incident_year = cleaned_data['last_incident_year']
        if type(incident_year) != int:
            return cleaned_data
        if incident_year < 1900:
            self.add_error('last_incident_year', ValidationError(
                DATE_ERRORS['no_past'],
            ))
    if 'last_incident_year' in cleaned_data and 'last_incident_month' in cleaned_data and 'last_incident_day' in cleaned_data:
        if datetime(incident_year, incident_month, incident_day) > datetime.now():
            self.add_error('last_incident_year', ValidationError(
                DATE_ERRORS['no_future'],
                params={'value': datetime(incident_year, incident_month, incident_day).strftime('%x')},
            ))
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
                'type': 'text',
                'maxlength': 2,
                'pattern': '[0-9]*',
                'inputmode': 'numeric',
                'label': DATE_QUESTIONS['last_incident_month']
            }),
            'last_incident_day': TextInput(attrs={
                'class': 'usa-input usa-input--small',
                'type': 'text',
                'maxlength': 2,
                'pattern': '[0-9]*',
                'inputmode': 'numeric',
            }),
            'last_incident_year': TextInput(attrs={
                'class': 'usa-input usa-input--medium',
                'required': True,
                'type': 'text',
                'minlength': 4,
                'maxlength': 4,
                'pattern': '[0-9]*',
                'inputmode': 'numeric',
            }),
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['last_incident_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['last_incident_month'].error_messages = {
            'invalid': DATE_ERRORS['month_invalid'],
            'required': DATE_ERRORS['month_required'],
        }
        self.fields['last_incident_month'].required = True
        self.fields['last_incident_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['last_incident_day'].error_messages = {
            'invalid': DATE_ERRORS['day_invalid'],
        }
        self.fields['last_incident_year'].label = DATE_QUESTIONS['last_incident_year']
        self.fields['last_incident_year'].error_messages = {
            'invalid': DATE_ERRORS['no_past'],
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
            ['hate_crime'] +\
            ['location_name', 'location_address_line_1', 'location_address_line_2',
                'location_city_town', 'location_state'] +\
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
            # location widgets
            {
                'location_name': TextInput(attrs={
                    'class': 'usa-input'
                }),
                'location_address_line_1': TextInput(attrs={
                    'class': 'usa-input'
                }),
                'location_address_line_2': TextInput(attrs={
                    'class': 'usa-input'
                }),
                'location_city_town': TextInput(attrs={
                    'class': 'usa-input'
                }),
                'location_state': Select(attrs={
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
                    'type': 'text',
                    'maxlength': 2,
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                    'required': False,
                }),
                'last_incident_day': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'text',
                    'maxlength': 2,
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                    'required': False,
                }),
                'last_incident_year': TextInput(attrs={
                    'class': 'usa-input usa-input--medium',
                    'type': 'text',
                    'minlength': 4,
                    'maxlength': 4,
                    'pattern': '[0-9]*',
                    'required': False,
                }),
            },
            {
                'crt_reciept_month': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'text',
                    'maxlength': 2,
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                    'required': True,
                }),
                'crt_reciept_day': TextInput(attrs={
                    'class': 'usa-input usa-input--small',
                    'type': 'text',
                    'maxlength': 2,
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                    'required': True,
                }),
                'crt_reciept_year': TextInput(attrs={
                    'class': 'usa-input usa-input--medium',
                    'type': 'text',
                    'minlength': 4,
                    'maxlength': 4,
                    'pattern': '[0-9]*',
                    'inputmode': 'numeric',
                    'required': True,
                }),
            },
        ]
        for widget in widget_list:
            all_widgets.update(widget)
        widgets = all_widgets

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        Contact.__init__(self, *args, **kwargs)
        # CRT views only
        self.fields['intake_format'] = ChoiceField(
            choices=(
                ('letter', 'letter'),
                ('phone', 'phone'),
                ('fax', 'fax'),
                ('email', 'email'),
            ),
            widget=UsaRadioSelect,
            error_messages={'required': INTAKE_FORMAT_ERROR},
            required=True,
        )
        self.fields['servicemember'] = TypedChoiceField(
            choices=SERVICEMEMBER_CHOICES,
            label=SERVICEMEMBER_QUESTION,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
        complaint_choices = PRIMARY_COMPLAINT_CHOICES_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_CHOICES
        self.fields['primary_complaint'] = TypedChoiceField(
            choices=complaint_choices,
            error_messages={'required': PRIMARY_COMPLAINT_ERROR},
            label=PRIMARY_REASON_QUESTION,
            widget=UsaRadioSelect,
            required=True,
        )
        self.fields['hate_crime'] = TypedChoiceField(
            choices=HATE_CRIME_CHOICES,
            label=HATE_CRIME_QUESTION,
            help_text=HATE_CRIME_HELP_TEXT,
            empty_value=None,
            widget=UsaRadioSelect,
            required=False,
        )
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
        self.fields['crt_reciept_day'].required = True
        self.fields['crt_reciept_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['crt_reciept_month'].required = True
        self.fields['crt_reciept_year'].label = DATE_QUESTIONS['last_incident_year']
        self.fields['crt_reciept_year'].required = True
        self.fields['location_name'].label = LOCATION_QUESTIONS['location_name']
        if 'violation_summary' in self.fields:
            self.fields['violation_summary'].widget.attrs['class'] = 'usa-textarea word-count-500'
            self.label_suffix = ''
            self.fields['violation_summary'].label = SUMMARY_QUESTION
            self.fields['violation_summary'].widget.attrs['aria-describedby'] = 'details-help-text'
            # CRT view only
            self.fields['violation_summary'].help_text = 'What did the person believe happened?'

    def clean(self):
        """Validating more than one field at a time can't be done in the model validation"""
        cleaned_data = super(ProForm, self).clean()
        return crt_date_cleaner(self, cleaned_data)


class ProfileForm(ModelForm):
    intake_filters = MultipleChoiceField(
        required=False,
        choices=SECTION_CHOICES_WITHOUT_LABELS,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'intake_filters'
        })
    )

    class Meta:
        model = Profile
        fields = [
            'intake_filters'
        ]

        labels = {
            'intake_filters': 'View sections'
        }

    def clean_intake_filters(self):
        # Clean intake_filters by removing list markup
        if 'intake_filters' in self.cleaned_data:
            new_filter = self.cleaned_data['intake_filters']
            new_filter = str(new_filter).strip('[').strip(']').replace("'", '').replace(' ', '')
            return new_filter


def reported_reason_proform():
    """
    Strip parentheses from the value description.
    """
    for (key, value) in PROTECTED_MODEL_CHOICES:
        new_value = value[:value.find('(') - 1] if '(' in value else value
        yield (key, new_value)


class CampaignSelect(Select):
    def __init__(self, campaigns, *args, **kwargs):
        """Takes an additional dictionary of uuid: Campaign."""
        self.campaigns = campaigns
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, *args, **kwargs):
        properties = super().create_option(name, value, *args, **kwargs)
        campaign = self.campaigns.get(value, None)
        return {
            **properties,
            'attrs': {
                **properties['attrs'],
                'data-archived': str(campaign.archived if campaign else False),
                **({'data-section': str(campaign.section)} if campaign and campaign.section else {}),
            },
        }


class Filters(ModelForm):

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        # Putting this field in __init__ allows the User QuerySet to be evaluated
        # (otherwise it breaks when this module is read during a migration)
        self.fields['assigned_to'] = ChoiceField(
            required=False,
            choices=[
                ('', ''),  # Default choice: empty
                ('-1', '(none)'),  # Custom choice: unassigned report.
                # Appends a queryset of active users, converted to a list of tuples
            ] + list(User.objects.filter(is_active=True).values_list('pk', 'username').order_by('username')),
            label=_("Assigned to"),  # This is overriden in templates as "Assigned"
            widget=Select(attrs={
                'name': 'assigned_to',
                'class': 'usa-input usa-select',
            })
        )

        campaigns = {
            campaign.uuid: campaign
            for campaign in
            Campaign.objects.filter(show_in_filters=True).order_by('internal_name').all()
        }
        campaign_choices = [
            (uuid, campaign.internal_name)
            for uuid, campaign in campaigns.items()
        ]
        self.fields['origination_utm_campaign'] = MultipleChoiceField(
            required=False,
            choices=[
                ('', ''),  # Default choice: empty (include everything)
                ('-1', '(none)'),  # Custom: No assigned campaign.
                *campaign_choices,
            ],
            label=_("Campaign"),
            widget=CampaignSelect(campaigns, attrs={
                'name': 'origination_utm_campaign',
                'class': 'usa-input usa-select',
            })
        )

    status = MultipleChoiceField(
        initial=(('new', 'New'), ('open', 'Open')),
        required=False,
        label='status',
        choices=STATUS_CHOICES,
        widget=UsaCheckboxSelectMultiple(),
    )
    location_state = MultipleChoiceField(
        required=False,
        label=_("Incident state"),
        choices=STATES_AND_TERRITORIES,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'location_state',
        }),
    )
    primary_statute = ChoiceField(
        required=False,
        label=_("Primary classification"),  # This is overridden in templates to the shorter "Classification"
        choices=add_empty_choice(STATUTE_CHOICES),
        widget=Select(attrs={
            'name': 'primary_statute',
            'class': 'usa-select',
            'aria-label': 'Primary Classification'
        })
    )
    per_page = ChoiceField(
        required=False,
        label=_("Records per page"),
        choices=add_empty_choice(PER_PAGE),
        widget=Select(attrs={
            'name': 'per_page',
            'class': 'usa-select',
            'aria-label': 'Records per page'
        })
    )
    grouping = ChoiceField(
        initial=('default', 'Default'),
        required=False,
        label=_("Grouping"),
        choices=add_empty_choice(GROUPING),
        widget=Select(attrs={
            'name': 'grouping',
            'class': 'usa-select',
            'aria-label': 'Grouping'
        })
    )
    summary = CharField(
        required=False,
        widget=TextInput(
            attrs={
                'class': 'usa-input',
                'name': 'summary',
                'placeholder': 'CRT summary',
                'aria-label': 'Complaint Summary'
            },
        ),
    )
    contact_phone = CharField(
        required=False,
        widget=TextInput(
            attrs={
                'class': 'usa-input',
                'name': 'contact_phone',
                'placeholder': 'Contact Phone Number',
                'aria-label': 'Contact Phone Number'
            },
        ),
    )
    create_date_start = DateField(
        required=False,
        label="From:",
        input_formats=('%Y-%m-%d'),
        widget=CrtDateInput(attrs={
            'class': 'usa-input',
            'name': 'create_date_start',
            'min': '2019-01-01',
            'placeholder': 'yyyy-mm-dd',
        }),
    )
    create_date_end = DateField(
        required=False,
        label="To:",
        input_formats=('%Y-%m-%d'),
        widget=CrtDateInput(attrs={
            'class': 'usa-input',
            'name': 'create_date_end',
            'min': '2019-01-01',
            'placeholder': 'yyyy-mm-dd',
        }),
    )
    proform_choices = PRIMARY_COMPLAINT_PROFORM_CHOICES_VOTING if is_voting_mode() else PRIMARY_COMPLAINT_PROFORM_CHOICES
    primary_complaint = MultipleChoiceField(
        required=False,
        label='Primary issue',
        choices=proform_choices,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'primary_issue',
        }),
    )
    reported_reason = MultipleChoiceField(
        required=False,
        label='Reported reason',
        choices=reported_reason_proform,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'reported_reason',
        }),
    )
    commercial_or_public_place = MultipleChoiceField(
        required=False,
        label='Relevant details',
        choices=COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'relevant_details',
        }),
    )
    hate_crime = MultipleChoiceField(
        required=False,
        label='Hate crime',
        choices=(('yes', 'Yes'),),
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'hate_crime',
        }),
    )
    servicemember = MultipleChoiceField(
        required=False,
        label='Servicemember',
        choices=(('yes', 'Yes'),),
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'servicemember',
        }),
    )
    intake_format = MultipleChoiceField(
        required=False,
        label='Intake type',
        choices=INTAKE_FORMAT_CHOICES,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'intake_format',
        }),
    )
    language = MultipleChoiceField(
        required=False,
        label='Report language',
        choices=settings.LANGUAGES,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'language',
        }),
    )
    referred = MultipleChoiceField(
        required=False,
        label='Secondary review',
        choices=((True, 'Yes'),),
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'referred'
        }),
    )
    correctional_facility_type = MultipleChoiceField(
        required=False,
        label='Prison type',
        choices=CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
        widget=UsaCheckboxSelectMultiple(attrs={
            'name': 'correctional_facility_type',
        }),
    )

    class Meta:
        model = Report
        fields = [
            'assigned_section',
            'contact_first_name',
            'contact_last_name',
            'location_city_town',
            'location_state',
            'location_name',
            'status',
            'assigned_to',
            'public_id',
            'primary_statute',
            'violation_summary',
            'primary_complaint',
            'contact_phone',
            'commercial_or_public_place',
            'hate_crime',
            'servicemember',
            'intake_format',
            'contact_email',
            'referred',
            'language',
            'correctional_facility_type',
        ]

        labels = {
            # These are CRT view only
            'contact_first_name': 'Contact first name',
            'contact_last_name': 'Contact last name',
            'location_city_town': 'Incident city',
            'location_state': 'Incident state',
            'location_name': 'Incident location name',
            'assigned_to': 'Assignee',
            'public_id': 'Complaint ID',
            'violation_summary': 'Personal description',
            'contact_email': 'Contact email',
        }

        widgets = {
            'assigned_section': CrtMultiSelect(attrs={
                'class': 'text-uppercase',
                'name': 'assigned_section'
            }),
            'contact_first_name': TextInput(attrs={
                'id': 'id_contact_first_name',
                'class': 'usa-input',
                'name': 'contact_first_name',
                'placeholder': labels['contact_first_name'],
                'aria-label': labels['contact_first_name']
            }),
            'contact_last_name': TextInput(attrs={
                'class': 'usa-input',
                'name': 'contact_last_name',
                'placeholder': labels['contact_last_name'],
                'aria-label': labels['contact_last_name']
            }),
            'location_city_town': TextInput(attrs={
                'class': 'usa-input',
                'name': 'location_city_town'
            }),
            'location_name': TextInput(attrs={
                'class': 'usa-input',
                'name': 'location_name',
                'placeholder': labels['location_name'],
                'aria-label': labels['location_name']
            }),
            'public_id': TextInput(attrs={
                'class': 'usa-input',
                'name': 'public_id',
                'placeholder': labels['public_id'],
                'aria-label': labels['public_id']
            }),
            'violation_summary': Textarea(attrs={
                'class': 'usa-textarea border-0',
                'name': 'violation_summary',
                'placeholder': labels['violation_summary'],
                'aria-label': labels['violation_summary']
            }),
            'contact_email': EmailInput(attrs={
                'class': 'usa-input',
                'name': 'contact_email',
                'placeholder': labels['contact_email'],
                'aria-label': labels['contact_email'],
            }),
        }
        error_messages = {
            'create_date': {
                'in_future': _("Create date cannot be in the future."),
            },
        }

    @property
    def get_section_filters(self):
        """
        Return set of sections received as query parameters which are also valid section choices
        """
        inbound_sections = set(self.data.getlist('assigned_section'))
        section_choices = {section for section, _ in self.fields['assigned_section'].choices}
        return inbound_sections.intersection(section_choices)


class ResponseActions(Form):

    def __init__(self, *args, **kwargs):
        self.report = kwargs.pop('instance')
        Form.__init__(self, *args, **kwargs)
        # set up select options with dataset attributes
        templates = ResponseTemplate.objects.order_by('title')
        data = {
            template.id: {
                'language': template.language,
            }
            for template in templates
        }
        attrs = {
            "aria-label": "template selection"
        }
        self.fields['selected_tab'] = CharField(widget=HiddenInput())
        self.fields['templates_default'] = ModelChoiceField(
            queryset=templates.filter(show_in_dropdown=True,
                                      referral_contact__isnull=True),
            empty_label="(no template chosen)",
            widget=DataAttributesSelect(data=data, attrs={
                **attrs,
                "class": "intake-select usa-select response-template-default",
            }),
            required=False,
        )
        self.fields['templates_referral'] = ModelChoiceField(
            queryset=templates.filter(show_in_dropdown=True,
                                      referral_contact__isnull=False),
            empty_label="(no template chosen)",
            widget=DataAttributesSelect(data=data, attrs={
                **attrs,
                "class": "intake-select usa-select response-template-referral",
            }),
            required=False,
        )


class ComplaintActions(ModelForm, ActivityStreamUpdater):
    report_closed = False
    CONTEXT_KEY = 'actions'
    assigned_to = ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        # crt view only
        label='Assigned to',
        required=False,
        widget=Select(attrs={
            'class': 'usa-input usa-select',
        })
    )
    referred = BooleanField(
        label='Secondary review',
        required=False,
        widget=CheckboxInput(attrs={
            'class': 'usa-checkbox__input',
            'aria-label': 'Secondary review',
        })
    )

    class Meta:
        model = Report
        fields = ['assigned_section', 'status', 'primary_statute',
                  'district', 'assigned_to', 'referred', 'dj_number']

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)

        self.fields['assigned_section'] = ChoiceField(
            widget=ComplaintSelect(
                label='Section',
                attrs={'class': 'usa-select crt-dropdown__data'},
            ),
            choices=SECTION_CHOICES_WITHOUT_LABELS,
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
                label='Primary classification',
                attrs={
                    'class': 'crt-dropdown__data',
                },
            ),
            choices=add_empty_choice(STATUTE_CHOICES, default_string=''),
            required=False
        )
        self.fields['district'] = ChoiceField(
            widget=ComplaintSelect(
                label='Judicial district',
                attrs={
                    'class': 'crt-dropdown__data',
                },
            ),
            choices=add_empty_choice(DISTRICT_CHOICES, default_string=''),
            required=False
        )
        self.fields['dj_number'] = CharField(
            widget=DjNumberWidget(attrs={'field_label': 'ICM DJ Number'}),
            required=False,
        )

    def get_actions(self):
        """
        Parse incoming changed data for activity stream entry
        If report has been closed, emit action for activity log
        """
        for field in self.changed_data:
            name = ' '.join(field.split('_')).capitalize()
            # rename primary statute if applicable
            if field == 'primary_statute':
                name = 'Primary classification'
            # rename referred if applicable
            if field == 'referred':
                name = 'Secondary review'
            if field == 'dj_number':
                name = 'ICM DJ Number'
            original = self.initial[field]
            changed = self.cleaned_data[field]
            # fix bug where id was showing up instead of user name
            if field == 'assigned_to':
                if original is None:
                    yield f"{name}:", f'"{changed}"'
                else:
                    original = User.objects.get(id=original)
            yield f"{name}:", f'Updated from "{original}" to "{changed}"'
        if self.report_closed:
            yield "Report closed and Assignee removed", f"Date closed updated to {self.instance.closed_date.strftime('%m/%d/%y %H:%M:%M %p')}"

    def update_activity_stream(self, user):
        """Send all actions to activity stream"""
        for verb, description in self.get_actions():
            action.send(
                user,
                verb=verb,
                description=description,
                target=self.instance
            )

    def success_message(self):
        """Prepare update success message for rendering in template"""
        def get_label(field):
            field = self.fields[field]
            # Some fields can't support the extra context label, and store it
            # on their attributes
            if attrs_label := field.widget.attrs.get('field_label', None):
                return attrs_label
            # Most standard fields will have a direct label.
            if hasattr(field.widget, 'label'):
                return field.widget.label
            return field.label
        updated_fields = [get_label(field) for field in self.changed_data]
        if len(updated_fields) == 1:
            message = f"Successfully updated {updated_fields[0]}."
        else:
            fields = ', '.join(updated_fields[:-1])
            fields += f', and {updated_fields[-1]}'
            message = f"Successfully updated {fields}."
        return message

    def save(self, commit=True):
        """
        If report.status is `closed`, set assigned_to to None.
        If this report was referred, set the section.
        """
        report = super().save(commit=False)
        if report.closed:
            report.closeout_report()
            self.report_closed = True
        if report.referred:
            report.referral_section = report.assigned_section
        elif report.referral_section:
            report.referral_section = ''
        if commit:
            report.save()
        return report


class CommentActions(ModelForm):
    class Meta:
        model = CommentAndSummary
        fields = ['note']
        error_messages = {
            'note': {
                'required': _('Comment cannot be empty'),
            },
        }

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['note'].max_length = 7000
        self.fields['note'].widget = Textarea(
            attrs={
                'class': 'usa-textarea',
                'id': 'id_note-comment',
            },
        )
        self.fields['note'].label = 'New comment'

    def update_activity_stream(self, user, report, verb):
        """Send all actions to activity stream"""
        action.send(
            user,
            verb=verb,
            description=self.instance.note,
            target=report
        )


class PrintActions(Form):
    CONTEXT_KEY = 'print_actions'

    options = MultipleChoiceField(
        initial=('correspondent', 'issue', 'description',),
        required=False,
        label='options',
        choices=PRINT_CHOICES,
        widget=UsaCheckboxSelectMultiple(),
    )


class BulkActionsForm(Form, ActivityStreamUpdater):
    EMPTY_CHOICE = 'Multiple'
    assigned_section = ChoiceField(
        label='Section',
        widget=ComplaintSelect(
            attrs={'class': 'usa-select crt-dropdown__data'},
        ),
        choices=add_empty_choice(SECTION_CHOICES_WITHOUT_LABELS, default_string=EMPTY_CHOICE),
        required=False
    )
    status = ChoiceField(
        widget=ComplaintSelect(
            attrs={'class': 'crt-dropdown__data'},
        ),
        choices=add_empty_choice(STATUS_CHOICES, default_string=EMPTY_CHOICE),
        required=False
    )
    primary_statute = ChoiceField(
        label='Primary classification',
        widget=ComplaintSelect(
            attrs={'class': 'crt-dropdown__data'},
        ),
        choices=add_empty_choice(STATUTE_CHOICES, default_string=EMPTY_CHOICE),
        required=False
    )
    district = ChoiceField(
        label='Judicial district',
        widget=ComplaintSelect(
            attrs={
                'class': 'crt-dropdown__data',
                'disabled': 'disabled'
            },
        ),
        choices=add_empty_choice(DISTRICT_CHOICES, default_string=EMPTY_CHOICE),
        required=False
    )
    assigned_to = ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        label='Assigned to',
        required=False
    )
    summary = CharField(
        required=False,
        max_length=7000,
        label='CRT summary',
        widget=Textarea(
            attrs={
                'rows': 3,
                'class': 'usa-textarea',
                'aria-label': 'Complaint summary'
            },
        ),
    )
    comment = CharField(
        required=True,
        max_length=7000,
        widget=Textarea(
            attrs={
                'rows': 3,
                'class': 'usa-textarea',
            },
        ),
    )

    def get_initial_values(record_query, keys):
        """
        Given a record query and a list of keys, determine if a key has a
        singular value within that query. Used to set initial fields
        for bulk update forms.
        """
        # make sure the queryset does not order by anything, otherwise
        # we will have difficulty getting distinct results.
        query = record_query.order_by()
        for key in keys:
            values = query.values_list(key, flat=True).distinct()
            if values.count() == 1:
                yield key, values[0]

    def __init__(self, query, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        # set initial values if applicable
        keys = ['assigned_section', 'status', 'primary_statute', 'district']
        for key, initial_value in BulkActionsForm.get_initial_values(query, keys):
            self.fields[key].initial = initial_value

    def get_updates(self):
        updates = {field: self.cleaned_data[field] for field in self.changed_data}
        # do not allow any fields to be unset. this may happen if the
        # user selects "Multiple".
        for key in ['assigned_section', 'status', 'primary_statute']:
            if key in updates and not updates[key]:
                updates.pop(key)
        # if section is changed, override assignee and status
        # explicitly, even if they are set by the user.
        if 'assigned_section' in updates:
            updates['primary_statute'] = None
            updates['assigned_to'] = ''
            updates['status'] = 'new'

        updates.pop('district', None)  # district is currently disabled (read-only)
        return updates

    def get_update_description(self):
        """
        Given a submitted form, emit a textual description of what was updated.
        """
        updates = self.get_updates()
        labels = {key: self.fields[key].label or key for key in updates}
        labels.pop('comment', None)  # required, so we can omit
        default_string = '{what} set to {item}'
        custom_strings = {
            'assigned to': 'assigned to {item}',
            'crt summary': 'summary updated',
        }
        descriptions = []
        for (key, value) in labels.items():
            what = value.lower()
            item = updates[key]
            string = custom_strings.get(what, default_string)
            description = string.format(**{'what': what, 'item': item or "''"})
            descriptions.append(description)
        if len(descriptions) > 1:
            descriptions[-1] = f'and {descriptions[-1]}'
        return ', '.join(descriptions) or 'comment added'

    def get_actions(self, report):
        """
        Parse incoming changed data for activity stream entry (tweaked for
        bulk update)
        """

        def field_changed(old, new):
            # if both are Falsy, nothing actually changed (None ~= "")
            if not old and not new:
                return False
            return old != new

        updates = self.get_updates()
        for field in updates:
            name = ' '.join(field.split('_')).capitalize()
            # rename primary statute if applicable
            if field == 'primary_statute':
                name = 'Primary classification'
            if field in ['summary', 'comment']:
                continue
            initial = getattr(report, field, 'None')

            if field_changed(initial, updates[field]):
                yield f"{name}:", f'Updated from "{initial}" to "{updates[field]}"'

    def update_activity_stream(self, user, report):
        """
        Send all actions to activity stream (tweaked for bulk update)
        """
        for verb, description in self.get_actions(report):
            add_activity(user, verb, description, report)

    def update(self, reports, user):
        """
        Bulk update given reports and update activity log for each report
        """
        updated_data = self.get_updates()
        comment_string = updated_data.pop('comment', None)
        summary_string = updated_data.pop('summary', None)

        # rebuild the reports queryset w/o sorts and annotations to avoid error on update
        report_ids = reports.values_list('pk', flat=True)
        reports = Report.objects.filter(pk__in=report_ids)

        # assemble the activities but don't commit until after the reports are updated
        activities = []
        for report in reports:
            activities.extend([{
                'user': user,
                'report': report,
                'verb': v,
                'description': d
            } for (v, d) in self.get_actions(report)])

        if comment_string:
            kwargs = {
                'is_summary': False,
                'note': comment_string,
                'author': user.username,
            }
            for report in reports:
                comment = CommentAndSummary.objects.create(**kwargs)
                report.internal_comments.add(comment)
                activities.append({'user': user, 'report': report, 'verb': 'Added comment: ', 'description': comment_string})

        if summary_string:
            kwargs = {
                'is_summary': True,
                'note': summary_string,
                'author': user.username,
            }
            # update the pre-existing summary if extant
            for report in reports:
                summary = report.get_summary
                if summary:
                    CommentAndSummary.objects.update_or_create(id=summary.id, defaults=kwargs)
                else:
                    summary = CommentAndSummary.objects.create(**kwargs)
                    report.internal_comments.add(summary)
                activities.append({'user': user, 'report': report, 'verb': 'Added summary: ', 'description': summary_string})

        if updated_data:
            updated_data['modified_date'] = datetime.now(timezone.utc)

        existing_reports_closed = []
        for report in reports:
            existing_reports_closed.append(report.closed)
        updated_number = reports.update(**updated_data)
        for index, report in enumerate(reports):
            if report.closed and not existing_reports_closed[index]:
                report.closeout_report()
                report.save()
                activities.append({'user': user, 'report': report, 'verb': "Report closed and Assignee removed", 'description': f"Date closed updated to {report.closed_date.strftime('%m/%d/%y %H:%M:%M %p')}"})
        for act in activities:
            add_activity(act['user'], act['verb'], act['description'], act['report'])

        return updated_number or len(reports)  # sometimes only a comment is added


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
                'title': CONTACT_PHONE_INVALID_MESSAGE
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

        self.fields['contact_phone'].error_messages = {'invalid': CONTACT_PHONE_INVALID_MESSAGE}

    def success_message(self):
        return self.SUCCESS_MESSAGE


class ReportEditForm(ProForm, ActivityStreamUpdater):
    CONTEXT_KEY = "details_form"
    FAIL_MESSAGE = "Failed to update complaint details."
    SUCCESS_MESSAGE = "Successfully updated complaint details."
    # Keeping these for archival data
    hatecrime = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'usa-checkbox__input'}))
    trafficking = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'usa-checkbox__input'}))

    # Summary fields
    summary = CharField(required=False, strip=True, widget=Textarea(attrs={'class': 'usa-textarea'}))
    summary_id = IntegerField(required=False, widget=HiddenInput())

    class Meta(ProForm.Meta):
        """
        Extend ProForm to capture field definitions from component forms, excluding those which should not be editable here
        """
        exclude = [
            'contact_address_line_1',
            'contact_address_line_2',
            'contact_city',
            'contact_email',
            'contact_first_name',
            'contact_last_name',
            'contact_phone',
            'contact_state',
            'contact_zip',
            'election_details',
            'intake_format',
            'origination_utm_campaign',
            'origination_utm_content',
            'origination_utm_medium',
            'origination_utm_source',
            'origination_utm_term',
            'unknown_origination_utm_campaign',
            'violation_summary',
        ]

    def success_message(self):
        return self.SUCCESS_MESSAGE

    def _set_to_select_widget(self, field):
        """Set the provided 'field's widget to Select"""
        self.fields[field] = TypedChoiceField(
            choices=self.fields[field].choices,
            widget=Select(attrs={'class': 'usa-select'}),
            required=False,
        )

    def __init__(self, *args, **kwargs):
        """
        Proform initializes all component forms, we'll skip that and define only the fields need for this form
        """
        ModelForm.__init__(self, *args, **kwargs)

        #  We're handling old hatecrimes_trafficking data with separate boolean fields
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
        self._set_to_select_widget('inside_correctional_facility')
        self._set_to_select_widget('correctional_facility_type')
        self._set_to_select_widget('commercial_or_public_place')

        # date fields
        self.fields['last_incident_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['last_incident_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['last_incident_year'].label = DATE_QUESTIONS['last_incident_year']
        self.fields['last_incident_day'].widget.required = False
        self.fields['last_incident_month'].widget.required = False
        self.fields['last_incident_year'].widget.required = False
        self.fields['crt_reciept_day'].label = DATE_QUESTIONS['last_incident_day']
        self.fields['crt_reciept_month'].label = DATE_QUESTIONS['last_incident_month']
        self.fields['crt_reciept_year'].label = DATE_QUESTIONS['last_incident_year']
        self.fields['crt_reciept_day'].widget.required = False
        self.fields['crt_reciept_month'].widget.required = False
        self.fields['crt_reciept_year'].widget.required = False

        # Summary fields
        summary = self.instance.get_summary
        if summary:
            self.fields['summary'].initial = summary.note
            self.fields['summary_id'].initial = summary.pk

    @cached_property
    def changed_data(self):
        changed_data = super().changed_data

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
        cleaned_data = super().clean()
        return self.clean_dependent_fields(cleaned_data)

    def update_activity_stream(self, user):
        """Generate activity log entry for summary if it was updated"""
        super().update_activity_stream(user)
        if 'summary' in self.changed_data:
            action.send(
                user,
                verb='Added summary: ' if self.summary_created else 'Updated summary: ',
                description=self.summary.note,
                target=self.instance
            )

    def save(self, user=None, commit=True):
        """
        If `summary` has changed, update or create the necessary CommentAndSummary
        """
        report = super().save(commit=True)
        if 'summary' in self.changed_data:
            summary_id = self.cleaned_data.get('summary_id')
            summary = self.cleaned_data.get('summary')
            summary_data = {'note': summary, 'author': user, 'is_summary': True}
            if summary_id:
                summary, created = CommentAndSummary.objects.update_or_create(id=summary_id, defaults=summary_data)
            else:
                summary = CommentAndSummary.objects.create(**summary_data)
                created = True
                report.internal_comments.add(summary)
            self.summary_created = created
            self.summary = summary
        return report


class AttachmentActions(ModelForm):
    class Meta:
        model = ReportAttachment
        fields = ['file', 'report']

        widgets = {
            'file': ClearableFileInput(attrs={
                'class': 'usa-input',
            }),
        }

    def save(self, commit=True):
        instance = ModelForm.save(self, commit=False)

        # this is the filename that the user sees
        instance.filename = instance.file.name

        # this is the filename that gets stored in S3
        suffix = datetime.now().strftime('%Y%m%d%H%M%S%f')
        instance.file.name = f'{instance.report.public_id}-{suffix}'

        if commit:
            instance.save()

        return instance

    def update_activity_stream(self, user, verb, instance):
        """Send all actions to activity stream"""
        action.send(
            user,
            verb=verb,
            description=instance.filename,
            target=instance.report
        )
