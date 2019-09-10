from datetime import datetime

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from phone_field import PhoneField

from .model_variables import (
    PRIMARY_COMPLAINT_CHOICES,
    PLACE_CHOICES,
    PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
    EMPLOYER_SIZE_CHOICES,
    PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
    PUBLIC_OR_PRIVATE_FACILITY_CHOICES,
    PUBLIC_OR_PRIVATE_HEALTHCARE_CHOICES,
    RESPONDENT_TYPE_CHOICES,
    WHEN_CHOICES,
    HOW_MANY_CHOICES,
    WHO_FOR_CHOICES,
    RELATIONSHIP_CHOICES,
    STATES_AND_TERRITORIES
)


def validate_phone(value):
    if value is not None or value != '':
        if len(value) < 10:
            raise ValidationError(
                ('"%(value)s" doesn\'t have enough numbers to be a phone number. Please double check your phone number and make sure you have an area code.'),
                params={'value': value},
            )


class InternalHistory(models.Model):
    note = models.CharField(max_length=500, null=False, blank=False,)
    create_date = models.DateTimeField(auto_now_add=True)
    # add author


class ProtectedClass(models.Model):
    protected_class = models.CharField(max_length=100, null=True, blank=True,)

    def __str__(self):
        return self.protected_class


class Report(models.Model):
    # contact form
    contact_first_name = models.CharField(max_length=225, null=True, blank=True)
    contact_last_name = models.CharField(max_length=225, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = PhoneField(validators=[validate_phone], null=True, blank=True, E164_only=False)
    # Not adding the address to the form yet
    contact_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    # what happened form
    primary_complaint = models.CharField(max_length=100, choices=PRIMARY_COMPLAINT_CHOICES, default=None)
    protected_class = models.ManyToManyField(ProtectedClass, blank=True)
    # where form
    place = models.CharField(max_length=100, choices=PLACE_CHOICES, default=None)
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
    # details form
    violation_summary = models.TextField()
    when = models.CharField(max_length=700, choices=WHEN_CHOICES, default=None)
    how_many = models.CharField(max_length=700, null=True, blank=True, choices=HOW_MANY_CHOICES, default=None)
    # TODO, upgrade to add validation https://pypi.org/project/django-phone-field/
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.violation_summary

    def was_published_recently(self):
        return self.create_date >= timezone.now() - datetime.timedelta(days=1)
