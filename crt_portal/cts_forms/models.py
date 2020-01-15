"""All models need to be added to signals.py for proper logging."""
from datetime import datetime

from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator
from django.utils.functional import cached_property

from .phone_regex import phone_validation_regex

from .model_variables import (
    PRIMARY_COMPLAINT_CHOICES,
    PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
    EMPLOYER_SIZE_CHOICES,
    PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
    PUBLIC_OR_PRIVATE_FACILITY_CHOICES,
    PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES,
    RESPONDENT_TYPE_CHOICES,
    STATES_AND_TERRITORIES,
    PROTECTED_MODEL_CHOICES,
    STATUS_CHOICES,
    SECTION_CHOICES,
    ELECTION_CHOICES,
    HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
)

import logging

logger = logging.getLogger(__name__)


class InternalHistory(models.Model):
    note = models.CharField(max_length=500, null=False, blank=False,)
    create_date = models.DateTimeField(auto_now_add=True)
    # add author


class ProtectedClass(models.Model):
    # add to be unique
    protected_class = models.CharField(max_length=100, null=True, blank=True, choices=PROTECTED_MODEL_CHOICES, unique=True)
    # used for ordering the choices on the form displays
    form_order = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.protected_class}'


class HateCrimesandTrafficking(models.Model):
    hatecrimes_trafficking_option = models.CharField(max_length=500, null=True, blank=True, choices=HATE_CRIMES_TRAFFICKING_MODEL_CHOICES, unique=True)

    def __str__(self):
        return self.hatecrimes_trafficking_option


class Report(models.Model):
    # Contact
    contact_first_name = models.CharField(max_length=225, null=True, blank=True)
    contact_last_name = models.CharField(max_length=225, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex)],
        max_length=225,
        null=True,
        blank=True
    )
    # Primary Issue
    primary_complaint = models.CharField(
        max_length=100,
        choices=PRIMARY_COMPLAINT_CHOICES,
        default='',
        blank=False
    )
    hatecrimes_trafficking = models.ManyToManyField(HateCrimesandTrafficking, blank=True)
    # Protected Class
    # See docs for notes on updating these values:
    # docs/maintenance_or_infrequent_tasks.md#change-protected-class-options
    protected_class = models.ManyToManyField(ProtectedClass)
    other_class = models.CharField(max_length=150, null=True, blank=True)
    # Details Summary
    violation_summary = models.TextField(max_length=7000, blank=False)
    status = models.TextField(choices=STATUS_CHOICES, default='new')
    assigned_section = models.TextField(choices=SECTION_CHOICES, default='ADM')
    # Incident location
    location_name = models.CharField(max_length=225, blank=False)
    location_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    location_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    location_city_town = models.CharField(max_length=700, blank=False)
    location_state = models.CharField(max_length=100, blank=False, choices=STATES_AND_TERRITORIES)
    create_date = models.DateTimeField(auto_now_add=True)
    # Incident location routing-specific fields
    election_details = models.CharField(choices=ELECTION_CHOICES, max_length=225, null=True, blank=True)
    public_or_private_employer = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, default=None)
    employer_size = models.CharField(max_length=100, null=True, choices=EMPLOYER_SIZE_CHOICES, default=None)
    # Incident date
    last_incident_year = models.PositiveIntegerField(MaxValueValidator(datetime.now().year, message="Date must not be in the future"))
    last_incident_day = models.PositiveIntegerField(MaxValueValidator(31, message='Day value too high'), null=True, blank=True)
    last_incident_month = models.PositiveIntegerField(MaxValueValidator(12, message="Month must be 12 or less"))

    @cached_property
    def last_incident_date(self):
        day = self.last_incident_day or 1
        return datetime(self.last_incident_year, self.last_incident_month, day)

    ###############################################################
    #   These fields have not been implemented in the form yet:   #
    ###############################################################
    # where form
    public_or_private_school = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, default=None)
    public_or_private_facility = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_FACILITY_CHOICES, default=None)
    public_or_private_healthcare = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES, default=None)
    # who form
    respondent_type = models.CharField(max_length=100, null=True, blank=True, choices=RESPONDENT_TYPE_CHOICES, default=None)
    respondent_contact_ask = models.BooleanField(null=True)
    respondent_name = models.CharField(max_length=225, null=True, blank=True)
    respondent_city = models.CharField(max_length=700, null=True, blank=True)
    respondent_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)

    def __str__(self):
        return f'{self.create_date} {self.violation_summary}'

    def __has_immigration_protected_classes(self, pcs):
        immigration_classes = [
            'Immigration/citizenship status (choosing this will not share your status)',
            'National origin (including ancestry and ethnicity)',
            'Language'
        ]
        is_not_included = set(pcs).isdisjoint(set(immigration_classes))

        if is_not_included:
            return False

        return True

    def assign_section(self):
        """See the SectionAssignmentTests for expected behaviors"""
        protected_classes = [n.protected_class for n in self.protected_class.all()]
        hatecrimes_options = [n.hatecrimes_trafficking_option for n in self.hatecrimes_trafficking.all()]

        if len(hatecrimes_options) > 0:
            return 'CRM'
        elif self.primary_complaint == 'voting' and 'Disability (including temporary or recovery)' not in protected_classes:
            return 'VOT'
        elif self.primary_complaint == 'workplace':
            if self.__has_immigration_protected_classes(protected_classes):
                return 'IER'
            elif 'Disability (including temporary or recovery)' not in protected_classes:
                return 'ELS'

        return 'ADM'
