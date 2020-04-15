"""All models need to be added to signals.py for proper logging."""
from datetime import datetime

from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator
from django.utils.functional import cached_property
from django.contrib.auth import get_user_model

from .phone_regex import phone_validation_regex

from .model_variables import (
    PRIMARY_COMPLAINT_CHOICES,
    PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
    EMPLOYER_SIZE_CHOICES,
    PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
    STATES_AND_TERRITORIES,
    PROTECTED_MODEL_CHOICES,
    STATUS_CHOICES,
    SECTION_CHOICES,
    ELECTION_CHOICES,
    HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
    SERVICEMEMBER_CHOICES,
    CORRECTIONAL_FACILITY_LOCATION_CHOICES,
    CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
    COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
    INTAKE_FORMAT_CHOICES,
    DISTRICT_CHOICES,
    STATUTE_CHOICES,
    DATE_ERRORS,
    PUBLIC_USER
)

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CommentAndSummary(models.Model):
    note = models.CharField(max_length=7000, null=False, blank=False,)
    author = models.CharField(max_length=1000, null=False, blank=False,)
    modified_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    is_summary = models.BooleanField(default=False)


class ProtectedClass(models.Model):
    protected_class = models.CharField(max_length=100, null=True, blank=True, choices=PROTECTED_MODEL_CHOICES, unique=True)
    # for display in the CRT views
    code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    # used for ordering the choices on the form displays
    form_order = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.protected_class}'


class HateCrimesandTrafficking(models.Model):
    hatecrimes_trafficking_option = models.CharField(max_length=500, null=True, blank=True, choices=HATE_CRIMES_TRAFFICKING_MODEL_CHOICES, unique=True)

    def __str__(self):
        return self.hatecrimes_trafficking_option


class JudicialDistrict(models.Model):
    zipcode = models.CharField(max_length=700, null=True, blank=True)
    city = models.CharField(max_length=700, null=True, blank=True)
    county = models.CharField(max_length=700, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    district_number = models.SmallIntegerField(null=True, blank=True)
    district_letter = models.CharField(max_length=2, null=True, blank=True)
    district = models.CharField(max_length=7)


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
    contact_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    contact_city = models.CharField(max_length=700, null=True, blank=True)
    contact_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_zip = models.CharField(max_length=10, null=True, blank=True)

    servicemember = models.CharField(max_length=4, null=True, blank=True, choices=SERVICEMEMBER_CHOICES)

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
    protected_class = models.ManyToManyField(ProtectedClass, blank=True)
    other_class = models.CharField(max_length=150, null=True, blank=True)

    # Details Summary
    violation_summary = models.TextField(max_length=7000, null=True, blank=True)
    status = models.TextField(choices=STATUS_CHOICES, default='new')
    assigned_section = models.TextField(choices=SECTION_CHOICES, default='ADM')

    # Incident location
    location_name = models.CharField(max_length=225, null=True, blank=True)
    location_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    location_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    location_city_town = models.CharField(max_length=700, null=True, blank=True)
    location_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)

    # Incident location routing-specific fields
    election_details = models.CharField(max_length=225, null=True, blank=True, default=None, choices=ELECTION_CHOICES)
    public_or_private_employer = models.CharField(max_length=100, null=True, default=None, choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES)
    employer_size = models.CharField(max_length=100, null=True, default=None, choices=EMPLOYER_SIZE_CHOICES)

    # By law
    inside_correctional_facility = models.CharField(max_length=255, null=True, blank=True, default=None, choices=CORRECTIONAL_FACILITY_LOCATION_CHOICES)
    correctional_facility_type = models.CharField(max_length=50, null=True, blank=True, default=None, choices=CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES)

    # Commercial or public space
    commercial_or_public_place = models.CharField(max_length=225, choices=COMMERCIAL_OR_PUBLIC_PLACE_CHOICES, null=True, default=None)
    other_commercial_or_public_place = models.CharField(max_length=150, blank=True, null=True, default=None)

    # Education location
    public_or_private_school = models.CharField(max_length=100, null=True, choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, default=None)

    # Incident date
    last_incident_year = models.PositiveIntegerField(MaxValueValidator(datetime.now().year, message=DATE_ERRORS['no_future']), null=True, blank=True)
    last_incident_day = models.PositiveIntegerField(MaxValueValidator(31, message=DATE_ERRORS['day_invalid']), null=True, blank=True)
    last_incident_month = models.PositiveIntegerField(MaxValueValidator(12, message=DATE_ERRORS['month_invalid']), null=True, blank=True,)

    # Internal comments
    internal_comments = models.ManyToManyField(CommentAndSummary)
    # Internal codes
    district = models.CharField(max_length=7, null=True, blank=True, choices=DISTRICT_CHOICES)
    primary_statute = models.CharField(max_length=7, null=True, blank=True, choices=STATUTE_CHOICES)

    # Metadata
    public_id = models.CharField(max_length=100, null=False, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    crt_reciept_year = models.PositiveIntegerField(MaxValueValidator(datetime.now().year), null=True, blank=True)
    crt_reciept_day = models.PositiveIntegerField(MaxValueValidator(31), null=True, blank=True)
    crt_reciept_month = models.PositiveIntegerField(MaxValueValidator(12), null=True, blank=True)
    intake_format = models.CharField(max_length=100, null=True, default=None, choices=INTAKE_FORMAT_CHOICES)
    author = models.CharField(max_length=1000, null=True, blank=True)

    @cached_property
    def last_incident_date(self):
        try:
            day = self.last_incident_day or 1
            date = datetime(self.last_incident_year, self.last_incident_month, day)
        except ValueError:
            date = None
        return date

    @cached_property
    def crt_reciept_date(self):
        day = self.crt_reciept_day or 1
        try:
            date = datetime(self.crt_reciept_year, self.crt_reciept_month, day)
        except ValueError:
            date = None
        return date

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

    def __is_not_disabled(self, pcs):
        return 'Disability (including temporary or recovery)' not in pcs

    def assign_section(self):
        """See the SectionAssignmentTests for expected behaviors"""
        protected_classes = [n.protected_class for n in self.protected_class.all()]
        hatecrimes_options = [n.hatecrimes_trafficking_option for n in self.hatecrimes_trafficking.all()]

        if len(hatecrimes_options) > 0:
            return 'CRM'

        elif self.primary_complaint == 'voting':
            if self.__is_not_disabled(protected_classes):
                return 'VOT'
            else:
                return 'DRS'

        elif self.primary_complaint == 'workplace':
            if self.__has_immigration_protected_classes(protected_classes):
                return 'IER'
            else:
                return 'ELS'

        elif self.primary_complaint == 'commercial_or_public':
            if not self.__is_not_disabled(protected_classes):
                return 'DRS'
            elif self.commercial_or_public_place == 'healthcare':
                return 'SPL'
            else:
                return 'HCE'

        elif self.primary_complaint == 'housing':
            return 'HCE'

        elif self.primary_complaint == 'education':
            if self.public_or_private_school == 'public' or self.public_or_private_school == 'not_sure':
                return 'EOS'
            elif self.__is_not_disabled(protected_classes):
                return 'EOS'
            elif self.public_or_private_school == 'private'and not self.__is_not_disabled(protected_classes):
                return 'DRS'

        elif self.primary_complaint == 'police':
            if self.__is_not_disabled(protected_classes) and self.inside_correctional_facility == 'inside':
                return 'SPL'
            elif self.__is_not_disabled(protected_classes) and self.inside_correctional_facility == 'outside':
                return 'CRM'
            else:
                return 'DRS'

        elif self.primary_complaint == 'something_else' and not self.__is_not_disabled(protected_classes):
            return 'DRS'

        return 'ADM'

    def assign_district(self):
        if self.location_city_town and self.location_state:
            city = self.location_city_town.upper().strip()
            district_query = JudicialDistrict.objects.filter(city=city, state=self.location_state)
            if len(district_query) > 0:
                return district_query[0].district

        return None

    @property
    def get_summary(self):
        """Return most recent summary provided by an intake specialist"""
        return self.internal_comments.filter(is_summary=True).order_by('-modified_date').first()
