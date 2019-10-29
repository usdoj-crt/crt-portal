from django.forms import ModelForm, CheckboxInput, \
    TypedChoiceField, TextInput, EmailInput, ModelMultipleChoiceField
from .question_group import QuestionGroup
from .widgets import UsaRadioSelect, UsaCheckboxSelectMultiple
from .models import Report, ProtectedClass
from .model_variables import EMPLOYER_SIZE_CHOICES, PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, RESPONDENT_TYPE_CHOICES, PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, PUBLIC_OR_PRIVATE_FACILITY_CHOICES, PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES, PROTECTED_CLASS_CHOICES, PROTECTED_CLASS_ERROR
from .phone_regex import phone_validation_regex

import logging

logger = logging.getLogger(__name__)


class Contact(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.label_suffix = ''

        self.fields['contact_first_name'].label = 'First name'
        self.fields['contact_last_name'].label = 'Last name'
        self.fields['contact_email'].label = 'Email address'
        self.fields['contact_phone'].label = 'Phone number'

        self.question_groups = [
            QuestionGroup(
                self,
                ('contact_first_name', 'contact_last_name'),
                group_name='Name',
                help_text="Leave the fields blank if you'd like to file anonymously",
            ),
            QuestionGroup(
                self,
                ('contact_email', 'contact_phone'),
                group_name='Contact information',
                help_text='You are not required to provide contact information, but it will help us if we need to gather more information about the incident you are reporting or to respond to your submission',
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
                'title': 'If you submit a phone number, please make sure to include between 7 and 15 digits. The characters "+", ")", "(", "-", and "." are allowed. Please include country code if entering an international phone number.'
            }),
        }


class Details(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['violation_summary'].widget.attrs['class'] = 'usa-textarea word-count-500'
        self.label_suffix = ''
        self.fields['violation_summary'].label = 'Tell us what happened'
        self.fields['violation_summary'].widget.attrs['aria-describedby'] = 'word_count_area'
        self.fields['violation_summary'].help_text = "Please include any details you have about time, location, or people involved with the event, names of witnesses or any materials that would support your description"

    class Meta:
        model = Report
        fields = [
            'violation_summary'
        ]


def retrieve_or_create_choices():
    choices = []
    for choice in PROTECTED_CLASS_CHOICES:
        try:
            choice_object = ProtectedClass.objects.get_or_create(protected_class=choice)
            choices.append(choice_object[0].pk)
        except:  # noqa
            # this has a concurrency issue for initial migrations
            logger.warning('ProtectedClass not loaded yet')
    return choices


class ProtectedClassForm(ModelForm):
    class Meta:
        model = Report
        fields = ['protected_class', 'other_class']
        widgets = {
            'protected_class': UsaCheckboxSelectMultiple,
            'other_class': TextInput(),
        }

    choices = retrieve_or_create_choices()
    protected_class = ModelMultipleChoiceField(
        error_messages={'required': PROTECTED_CLASS_ERROR},
        required=True,
        queryset=ProtectedClass.objects.filter(pk__in=choices).order_by('form_order'),
    )
    other_class = TextInput()

    # Overriding __init__ here allows us to provide initial data for 'protected_class' field
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        choices = retrieve_or_create_choices()
        self.fields['protected_class'].queryset = ProtectedClass.objects.filter(pk__in=choices).order_by('-form_order')
        choices = retrieve_or_create_choices()
        self.fields['protected_class'] = ModelMultipleChoiceField(
            error_messages={'required': 'Please make a selection to continue. If none of these apply to your situation, please select "Other reason" and explain.'},
            required=True,
            queryset=ProtectedClass.objects.filter(pk__in=choices).order_by('form_order'),
            widget=UsaCheckboxSelectMultiple,
        )
        self.fields['protected_class'].label = 'Do you believe you were treated this way because of any of the following characteristics or statuses that apply to you?'
        self.fields['protected_class'].help_text = 'Civil rights laws protects individuals from being discriminated against based on race, color, sex, religion, and other characteristics.'
        self.fields['other_class'].label = 'Other reason'
        self.fields['other_class'].help_text = 'Please describe "Other reason"'
        self.fields['other_class'].widget.attrs['class'] = 'usa-input word-count-10'


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
