"""All models need to be added to signals.py for proper logging."""
from django.db import models
from django.core.validators import RegexValidator

from .phone_regex import phone_validation_regex

from .model_variables import (
    PRIMARY_COMPLAINT_CHOICES,
    PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
    EMPLOYER_SIZE_CHOICES,
    PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
    PUBLIC_OR_PRIVATE_FACILITY_CHOICES,
    PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES,
    RESPONDENT_TYPE_CHOICES,
    WHEN_CHOICES,
    HOW_MANY_CHOICES,
    STATES_AND_TERRITORIES,
    PROTECTED_MODEL_CHOICES,
    STATUS_CHOICES,
    SECTION_CHOICES,
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
        return self.protected_class


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
    ###############################################################
    #   These fields have not been implemented in the form yet:   #
    ###############################################################
    # where form
    public_or_private_employer = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES, default=None)
    employer_size = models.CharField(max_length=100, null=True, choices=EMPLOYER_SIZE_CHOICES, default=None)
    public_or_private_school = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, default=None)
    public_or_private_facility = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_FACILITY_CHOICES, default=None)
    public_or_private_healthcare = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES, default=None)
    # who form
    respondent_type = models.CharField(max_length=100, null=True, blank=True, choices=RESPONDENT_TYPE_CHOICES, default=None)
    respondent_contact_ask = models.BooleanField(null=True)
    respondent_name = models.CharField(max_length=225, null=True, blank=True)
    respondent_city = models.CharField(max_length=700, null=True, blank=True)
    respondent_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    # previous details form
    when = models.CharField(max_length=700, choices=WHEN_CHOICES, default=None, null=True)
    how_many = models.CharField(max_length=700, null=True, blank=True, choices=HOW_MANY_CHOICES, default=None)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.create_date} {self.violation_summary}'

    def assign_section(self):
        protected_classes = [n.protected_class for n in self.protected_class.all()]

        if self.primary_complaint == 'voting' and 'Disability (including temporary or recovery)' not in protected_classes:
            return 'VOT'

        return 'ADM'
