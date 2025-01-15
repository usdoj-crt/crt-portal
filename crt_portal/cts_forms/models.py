"""All models need to be added to signals.py for proper logging."""
from typing import Optional
import logging
import time
import uuid
from datetime import datetime, timedelta
from babel.dates import format_date

import markdown
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import connection, models, transaction, migrations
from django.db.models import fields
from django.template import Context, Template
from django.urls import reverse
from django.utils import translation
from django.utils.functional import cached_property
from django.utils.html import escape
from django.contrib.auth.models import Group

from utils import sanitize
from utils.markdown_extensions import get_optionals, OptionalExtension, OptionalProcessor

from shortener.models import ShortenedURL

from .managers import ActiveProtectedClassChoiceManager
from .model_variables import (BATCH_STATUS_CHOICES, CLOSED_STATUS,
                              COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
                              CONTACT_PHONE_INVALID_MESSAGE,
                              CORRECTIONAL_FACILITY_LOCATION_CHOICES,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
                              DATE_ERRORS, REPORT_DISPOSITION_STATUS_CHOICES, DISTRICT_CHOICES, ELECTION_CHOICES,
                              EMPLOYER_SIZE_CHOICES, HATE_CRIME_CHOICES,
                              HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
                              INTAKE_FORMAT_CHOICES, PRIMARY_COMPLAINT_CHOICES,
                              NOTIFICATION_CADENCE_CHOICES,
                              PROTECTED_MODEL_CHOICES,
                              PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
                              PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
                              SECTION_CHOICES, SECTION_CHOICES_ES,
                              SECTION_CHOICES_KO,
                              SECTION_CHOICES_TL,
                              SECTION_CHOICES_VI,
                              SECTION_CHOICES_ZH_HANS,
                              SECTION_CHOICES_ZH_HANT,
                              SECTION_CHOICES_WITHOUT_LABELS,
                              SERVICEMEMBER_CHOICES,
                              STATES_AND_TERRITORIES, STATUS_CHOICES,
                              STATUTE_CHOICES)
from .phone_regex import phone_validation_regex
import pytz
from .validators import validate_file_attachment, validate_email_address, validate_dj_number

logger = logging.getLogger(__name__)
User = get_user_model()


def get_system_user():
    return User.objects.get(username='system.user')


class SavedSearch(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, help_text="The name of the search as it will appear in lists and dropdowns.")
    shortened_url = models.ForeignKey(ShortenedURL, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(max_length=1000, null=True, blank=True)
    query = models.TextField(null=False, blank=False, help_text="The encoded search represented as a URL querystring for the /form/view page.", default='')
    auto_close = models.BooleanField(default=False, null=False, help_text="Whether to automatically close incoming reports that match this search. Only applies to new submissions.")
    auto_close_reason = models.CharField(max_length=255, null=True, blank=True, help_text="The reason to add to the report summary when auto-closing. Will be filled in the following blank: 'Report automatically closed on submission because ____'")
    override_section_assignment = models.BooleanField(default=False, null=False, help_text="Whether to override the section assignment for all reports with this campaign")
    override_section_assignment_with = models.TextField(choices=SECTION_CHOICES, null=True, blank=True, help_text="If set, this will override the section assignment for all reports with this campaign. This can be used to 'tweak' the routing logic based on Personal Description, etc.")
    section = models.TextField(choices=SECTION_CHOICES, null=True, blank=True, default=None, help_text="The section to which this saved search applies.")
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    shared = models.BooleanField(default=False, null=False, help_text="Whether the search is viewable and editable by the rest of the portal users.")

    def get_absolute_url(self):
        return f'/form/view?{self.query}'

    def _set_short_url(self):
        if not self.query or not self.name:
            return

        shortname = ShortenedURL.urlify(self.name, prefix='search/')
        destination = self.get_absolute_url()

        if not self.shortened_url:
            self.shortened_url = ShortenedURL(shortname=shortname,
                                              destination=destination,
                                              enabled=True)
            self.shortened_url.save()
            return

        if self.shortened_url.shortname != shortname:
            self.shortened_url.delete()
            self.shortened_url = ShortenedURL(shortname=shortname,
                                              destination=destination,
                                              enabled=True)
            self.shortened_url.save()
            return

        if self.shortened_url.destination != destination:
            self.shortened_url.destination = destination
            self.shortened_url.save()

    def save(self, *args, **kwargs):
        self._set_short_url()
        super().save(*args, **kwargs)


class GroupPreferences(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group_preferences')
    saved_searches = models.JSONField(default=dict, blank=True, help_text="Contains the notification cadence for each saved search. The key is the saved search ID, and the value is the cadence.")
    saved_searches_threshold = models.JSONField(default=dict, blank=True, help_text="The threshold of results to trigger a notification for each search defaulting to 0 if none is set.")
    admins = models.ManyToManyField(User, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    intake_filters = models.TextField(max_length=500, blank=True)
    section = models.TextField(choices=SECTION_CHOICES, null=True, blank=True, default=None)

    def __str__(self):
        return str(self.user)


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    assigned_to = models.CharField('Assigned to a report', choices=NOTIFICATION_CADENCE_CHOICES, default='none')

    saved_searches = models.JSONField(default=dict, blank=True, help_text="Contains the notification cadence for each saved search. The key is the saved search ID, and the value is the cadence.")
    saved_searches_last_checked = models.JSONField(default=dict, blank=True, help_text="The last time each search was checked for new reports.")
    saved_searches_threshold = models.JSONField(default=dict, blank=True, help_text="The threshold of results to trigger a notification for each search.")
    saved_searches_count = models.JSONField(default=dict, blank=True, help_text="The total result counts of each search since the last threshold notification was sent.")

    def __getattr__(self, name):
        if name == 'saved_search_new' or name == 'saved_search_new_threshold':
            return 'none'
        if name.startswith('saved_search_'):
            return self.saved_searches.get(name.split('_')[-1], 'none')
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == 'saved_search_new' or name == 'saved_search_new_threshold':
            return
        if name.startswith('saved_search_') and name.endswith('_threshold'):
            search_id = name.split('_')[2]
            self.saved_searches_threshold[search_id] = value
            return
        elif name.startswith('saved_search_'):
            search_id = name.split('_')[-1]
            self.saved_searches[search_id] = value
            return
        super().__setattr__(name, value)

    def __str__(self):
        return str(self.user)


class ScheduledNotification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_digests')
    # An example "notifications":
    # {
    #   'assigned_to': [
    #     {
    #       'report': {
    #         'id': 1,
    #       }
    #     }
    #   ],
    #   'saved_search_1': {  # Where '1' is the ID of a SavedSearch object
    #     'name': 'Test search',
    #     'new_reports': 100,
    #   }
    # }
    notifications = models.JSONField()
    frequency = models.CharField(max_length=100, choices=NOTIFICATION_CADENCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_for = models.DateTimeField()
    was_sent = models.BooleanField(default=False)

    @classmethod
    def find_for(cls, recipient: User, frequency: str):
        if frequency == 'daily':
            scheduled_for = datetime.now() + timedelta(days=1)
        elif frequency == 'weekly':
            scheduled_for = datetime.now() + timedelta(days=7)
        elif frequency == 'threshold':
            scheduled_for = datetime.now() + timedelta(days=1)
        else:
            raise ValueError(f'Invalid frequency: {frequency}')

        scheduled, created = cls.objects.get_or_create(
            recipient=recipient,
            frequency=frequency,
            was_sent=False,
            defaults={
                'notifications': {},
                'scheduled_for': scheduled_for,
            },
        )
        return scheduled

    @classmethod
    def find_ready_to_send(cls):
        return cls.objects.filter(
            scheduled_for__lte=datetime.now(),
            was_sent=False,
        )


class CommentAndSummary(models.Model):
    note = models.CharField(max_length=7000, null=False, blank=False,)
    author = models.CharField(max_length=1000, null=False, blank=False,)
    modified_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    is_summary = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Comments and summaries'


class ProtectedClass(models.Model):
    protected_class = models.CharField(max_length=100, null=True, blank=True, choices=PROTECTED_MODEL_CHOICES, unique=True)
    value = models.CharField(max_length=100, blank=True, choices=PROTECTED_MODEL_CHOICES, unique=True)
    # for display in the CRT views
    code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    # used for ordering the choices on the form displays
    form_order = models.IntegerField(null=True, blank=True)

    objects = models.Manager()
    active_choices = ActiveProtectedClassChoiceManager()

    def __str__(self):
        return self.get_value_display()

    class Meta:
        verbose_name_plural = 'Protected classes'


# Not in use- but need to preserving historical data
class HateCrimesandTrafficking(models.Model):
    hatecrimes_trafficking_option = models.CharField(max_length=500, null=True, blank=True, choices=HATE_CRIMES_TRAFFICKING_MODEL_CHOICES, unique=True)
    value = models.CharField(max_length=500, blank=True, choices=HATE_CRIMES_TRAFFICKING_MODEL_CHOICES, unique=True)

    def __str__(self):
        return self.get_value_display()

    class Meta:
        verbose_name = 'Hate crime and trafficking'
        verbose_name_plural = 'Hate crimes and trafficking'


class JudicialDistrict(models.Model):
    zipcode = models.CharField(max_length=700, null=True, blank=True)
    city = models.CharField(max_length=700, null=True, blank=True)
    county = models.CharField(max_length=700, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    district_number = models.SmallIntegerField(null=True, blank=True)
    district_letter = models.CharField(max_length=2, null=True, blank=True)
    district = models.CharField(max_length=7)


class RoutingSection(models.Model):
    class Meta:
        verbose_name = 'Section POC'
        verbose_name_plural = 'Section POCs'
    section = models.TextField(choices=SECTION_CHOICES_WITHOUT_LABELS, default='ADM', unique=True)
    names = models.CharField(verbose_name='Routing Section POCs', max_length=700, null=False, blank=False, default='')
    retention_section_pocs = models.CharField(verbose_name='Retention Section POCs', max_length=700, null=False, blank=False, default='')

    def get_pocs(self, purpose='routing'):
        if purpose == 'retention':
            return self.retention_section_pocs
        if purpose == 'routing':
            return self.names
        raise ValueError(f'Invalid section contact purpose: {purpose}')

    def __str__(self):
        return self.section


class ApplicationContact(models.Model):
    name = models.CharField(max_length=250, null=False, blank=False)
    email = models.CharField(max_length=250, null=False, blank=False)
    order = models.IntegerField(default=0, help_text="The order in which to show the name, lower numbers first. If two names have the same order number, they might change positions.")

    def __str__(self):
        return f'{self.name} ({self.email})'


class RoutingStepOneContact(models.Model):
    contacts = models.TextField(max_length=700, null=False, blank=False)


class VotingMode(models.Model):
    toggle = models.BooleanField(default=False)


def get_translation(translated_text_json, language=None):
    """Gets a translated string from translated text (see make_translated_text)."""
    if not language:
        language = translation.get_language()

    translations = translated_text_json or {}
    en = translations.get('en')
    translated = translations.get(language)
    return translated or en or ''


def validate_translated_text(language_json):
    """Validates a JSONField as a Dict[LanguageCode, str]."""
    allowed_codes = {code for code, name in settings.LANGUAGES}
    for code, translated in language_json.items():
        if code not in allowed_codes:
            raise ValidationError(f'Unrecognized language code: {code}')
        if not isinstance(translated, str):
            raise ValidationError(f'Translation for {code} must be a string')


def make_translated_text():
    """Creates a translation dictionary for use in JSONField(default)."""
    return {
        code: ''
        for code, name
        in settings.LANGUAGES
    }


class BannerMessage(models.Model):
    order = models.IntegerField(default=0, help_text="The order in which to show the message, lower numbers first. If two messages have the same order number, they might change positions.")
    show = models.BooleanField(default=False, help_text="Whether to show the message on the public landing page.")
    kind = models.CharField(
        max_length=10, null=False, blank=False, default='warning',
        choices=(('notice', 'notice'), ('alert', 'alert'), ('emergency', 'emergency')))
    markdown_content = models.JSONField(null=False, help_text="Markdown to render and display in the banner.", default=make_translated_text, validators=[validate_translated_text])

    def english(self):
        return self.markdown_content.get('en', '')

    def as_html(self):
        translated = get_translation(self.markdown_content)
        return markdown.markdown(translated, extensions=['extra', 'sane_lists', 'admonition', 'nl2br'])


class ReferralContact(models.Model):
    machine_name = models.CharField(max_length=500, null=False, unique=True, blank=False, help_text="A short, non-changing name to be used in template code.")
    name = models.CharField(max_length=500, null=False, unique=True, blank=False, help_text="A short name to show in dropdown fields.")
    notes = models.TextField(max_length=7000, null=False, blank=True, help_text="Internal notes about how to use this referral information.")
    addressee_text = models.TextField(max_length=7000, null=False, blank=True, help_text="What to print on printed referral forms.")
    addressee_emails = models.TextField(max_length=7000, null=False, blank=True, help_text="A comma-separated list of emails to include on email referrals (for example: 'a@a.gov, b@b.gov')")
    show_as_referral = models.BooleanField(default=True, null=False, help_text="Whether to list this contact as a referral option.")
    variable_text = models.JSONField(null=False, help_text="Text to display when using the {{ referral_text }} variable in Response Templates.", default=make_translated_text, validators=[validate_translated_text])

    def clean_addressee_emails(self):
        return [
            addressee.strip()
            for addressee
            in self.addressee_emails.split(',')
            if addressee
        ]

    def __str__(self):
        return self.name


class Campaign(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    section = models.TextField(choices=SECTION_CHOICES, null=True)
    internal_name = models.CharField(max_length=100, null=False, unique=True, blank=False, help_text="The non-publicly-facing name for this campaign")
    description = models.TextField(max_length=1000, null=False, blank=True)
    show_in_filters = models.BooleanField(default=True, null=False)
    archived = models.BooleanField(default=False, null=False)

    def get_absolute_url(self):
        return f'/report?utm_campaign={self.uuid}'

    def __str__(self):
        return self.internal_name


class RetentionSchedule(models.Model):

    class Meta:
        permissions = (
            ("assign_retentionschedule", "Can assign retention schedules to reports"),
            ("approve_disposition", "Can approve disposition of reports"),
        )

    name = models.CharField(max_length=255, null=False, blank=False, help_text="The name of the schedule that will be shown to intake specialists in dropdowns.")
    order = models.IntegerField(default=0, help_text="The order in which to show the schedules, lower numbers first. If two schedules have the same order number, they might change positions.")
    description = models.TextField(max_length=7000, null=False, blank=True, help_text="Internal notes, shown only here, about this schedule.")
    tooltip = models.CharField(max_length=255, null=False, blank=True, help_text="The text to show in the tooltip for this schedule.")
    retention_years = models.IntegerField(null=False, blank=False, help_text="The number of years to retain reports with this schedule (following their closure). Set to 0 for permanent retention.")
    da_number = models.CharField(max_length=255, null=False, blank=False, help_text="The disposition authority number for this schedule (assigned by NARA).")
    is_retired = models.BooleanField(default=False, null=False, help_text="Whether this schedule is no longer active (show as a retired / expired schedule)")

    def __str__(self):
        return self.name


class EeocOffice(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, help_text="The name of the EEOC office that will be shown to intake specialists in dropdowns.")
    order = models.IntegerField(default=0, help_text="The order in which to show the offices, lower numbers first. If two offices have the same order number, they might change positions.")
    address_line_1 = models.CharField(max_length=255, null=False, blank=False)
    address_line_2 = models.CharField(max_length=255, null=False, blank=True)
    address_city = models.CharField(max_length=255, null=False, blank=False)
    address_state = models.CharField(max_length=100, null=False, blank=False, choices=STATES_AND_TERRITORIES)
    address_zip = models.CharField(max_length=10, null=False, blank=False)
    show = models.BooleanField(default=True, null=False, help_text="Whether to show this office in the list of EEOC offices.")
    url = models.CharField(max_length=255, null=False, blank=False, help_text="A link to the page that contains the contact information associated with this EEOC Office. Ex: https://www.eeoc.gov/field-office/atlanta/location")

    def __str__(self):
        return self.name


class Tag(models.Model):

    class Meta:
        permissions = (
            ("assign_tag", "Can assign tags to reports"),
        )

    name = models.CharField(max_length=255, null=False, blank=False, help_text="The name of the tag that will be shown throughout the app.")
    section = models.TextField(choices=SECTION_CHOICES, null=True, blank=True, default=None, help_text="The section to which this tag applies. If set, this tag will only be available to reports in this section.")
    tooltip = models.CharField(max_length=255, null=False, blank=True, help_text="The text to show in the tooltip for this tag.")
    description = models.TextField(max_length=7000, null=False, blank=True, help_text="Long-form notes about this tag, not shown on most pages.")
    show_in_lists = models.BooleanField(default=False, null=False, help_text="Whether to show this tag in the list page and dropdowns")

    def __str__(self):
        return self.name


class ReportManager(models.Manager):
    def get_queryset(self):
        return super(ReportManager, self).get_queryset().filter(disposed=False)


class AllReportManager(models.Manager):
    def get_queryset(self):
        return super(AllReportManager, self).get_queryset()


# NOTE: If you add fields to report, they'll automatically be set to empty on the edit form. Make sure to address any additions in ReportEditForm as well!
class Report(models.Model):

    objects = ReportManager()
    all_objects = AllReportManager()

    PRIMARY_COMPLAINT_DEPENDENT_FIELDS = {
        'workplace': ['public_or_private_employer', 'employer_size'],
        'education': ['public_or_private_school'],
        'police': ['inside_correctional_facility', 'correctional_facility_type'],
        'commercial_or_public': ['commercial_or_public_place', 'other_commercial_or_public_place']
    }

    # Contact
    contact_first_name = models.CharField(max_length=225, null=True, blank=True)
    contact_last_name = models.CharField(max_length=225, null=True, blank=True)
    contact_email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    contact_phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )
    contact_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    contact_city = models.CharField(max_length=700, null=True, blank=True)
    contact_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_zip = models.CharField(max_length=10, null=True, blank=True)
    contact_inmate_number = models.CharField(max_length=225, null=True, blank=True)
    by_repeat_writer = models.BooleanField(default=False)

    # Additional contact slots.
    # Not especially proud of this duplication, but having nested or inline models circumvents things like disposition, form rendering, javascript for editing, etc.
    # This duplication here reduces the complexity of all of that downstream code:
    contact_2_kind = models.CharField(max_length=225, null=True, blank=True)
    contact_2_name = models.CharField(max_length=225, null=True, blank=True)
    contact_2_email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    contact_2_phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )
    contact_2_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_2_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    contact_2_city = models.CharField(max_length=700, null=True, blank=True)
    contact_2_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_2_zip_code = models.CharField(max_length=10, null=True, blank=True)

    contact_3_kind = models.CharField(max_length=225, null=True, blank=True)
    contact_3_name = models.CharField(max_length=225, null=True, blank=True)
    contact_3_email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    contact_3_phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )
    contact_3_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_3_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    contact_3_city = models.CharField(max_length=700, null=True, blank=True)
    contact_3_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_3_zip_code = models.CharField(max_length=10, null=True, blank=True)

    contact_4_kind = models.CharField(max_length=225, null=True, blank=True)
    contact_4_name = models.CharField(max_length=225, null=True, blank=True)
    contact_4_email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    contact_4_phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )
    contact_4_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    contact_4_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    contact_4_city = models.CharField(max_length=700, null=True, blank=True)
    contact_4_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    contact_4_zip_code = models.CharField(max_length=10, null=True, blank=True)

    servicemember = models.CharField(max_length=4, null=True, blank=True, choices=SERVICEMEMBER_CHOICES)

    eeoc_charge_number = models.CharField(max_length=225, null=True, blank=True)
    eeoc_office = models.ForeignKey(EeocOffice, blank=True, null=True, on_delete=models.SET_NULL)

    # Primary Issue
    primary_complaint = models.CharField(
        max_length=100,
        choices=PRIMARY_COMPLAINT_CHOICES,
        default='',
        blank=False
    )

    hate_crime = models.CharField(max_length=4, null=True, blank=True, choices=HATE_CRIME_CHOICES)

    dj_number = models.CharField(
        validators=[validate_dj_number],
        max_length=256,
        null=True,
        blank=True,
    )

    # Protected Class
    # See docs for notes on updating these values:
    # docs/maintenance_or_infrequent_tasks.md#change-protected-class-options
    protected_class = models.ManyToManyField(ProtectedClass, blank=True)
    other_class = models.CharField(max_length=150, null=True, blank=True)

    # Details Summary
    violation_summary = models.TextField(max_length=7000, null=True, blank=True)
    status = models.TextField(choices=STATUS_CHOICES, default='new')
    report_disposition_status = models.TextField(choices=REPORT_DISPOSITION_STATUS_CHOICES, null=True, blank=True)
    assigned_section = models.TextField(choices=SECTION_CHOICES, default='ADM')

    # Incident location
    location_name = models.CharField(max_length=225, null=True, blank=True)
    location_address_line_1 = models.CharField(max_length=225, null=True, blank=True)
    location_address_line_2 = models.CharField(max_length=225, null=True, blank=True)
    location_city_town = models.CharField(max_length=700, null=True, blank=True)
    location_state = models.CharField(max_length=100, null=True, blank=True, choices=STATES_AND_TERRITORIES)
    location_zipcode = models.CharField(max_length=10, null=True, blank=True)

    # Incident location routing-specific fields
    election_details = models.CharField(max_length=225, null=True, blank=True, default=None, choices=ELECTION_CHOICES)
    public_or_private_employer = models.CharField(max_length=100, null=True, blank=True, default=None, choices=PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES)
    employer_size = models.CharField(max_length=100, null=True, blank=True, default=None, choices=EMPLOYER_SIZE_CHOICES)

    # By law
    inside_correctional_facility = models.CharField(max_length=255, null=True, blank=True, default=None, choices=CORRECTIONAL_FACILITY_LOCATION_CHOICES)
    correctional_facility_type = models.CharField(max_length=50, null=True, blank=True, default=None, choices=CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES)

    # Commercial or public space
    commercial_or_public_place = models.CharField(max_length=225, choices=COMMERCIAL_OR_PUBLIC_PLACE_CHOICES, null=True, blank=True, default=None)
    other_commercial_or_public_place = models.CharField(max_length=150, blank=True, null=True, default=None)

    # Education location
    public_or_private_school = models.CharField(max_length=100, null=True, blank=True, choices=PUBLIC_OR_PRIVATE_SCHOOL_CHOICES, default=None)

    # Incident date
    last_incident_year = models.PositiveIntegerField(MaxValueValidator(datetime.now().year, message=DATE_ERRORS['no_future']), null=True, blank=True)
    last_incident_day = models.PositiveIntegerField(MaxValueValidator(31, message=DATE_ERRORS['day_invalid']), null=True, blank=True)
    last_incident_month = models.PositiveIntegerField(MaxValueValidator(12, message=DATE_ERRORS['month_invalid']), null=True, blank=True,)

    # Internal comments
    internal_comments = models.ManyToManyField(CommentAndSummary)
    # Internal codes
    district = models.CharField(max_length=7, null=True, blank=True, choices=DISTRICT_CHOICES)
    primary_statute = models.CharField(max_length=7, null=True, blank=True, choices=STATUTE_CHOICES)

    # Origination info (utm campaigns, etc) about where the report came from.
    # Identifies which site sent the traffic.
    origination_utm_source = models.CharField(max_length=100, null=True, blank=True, help_text="Identifies which site the traffic came from, e.g. justice.gov/crt or ada.gov")
    # Identifies what type of link was used, such as cost per click or email.
    origination_utm_medium = models.CharField(max_length=100, null=True, blank=True, help_text="What channel (avenue of communication) was used, such as social, email, web, mail, etc")
    # Identifies a specific product promotion or strategic campaign.
    # For Portal specifically, this will be a uuid tied to a Campaign object.
    origination_utm_campaign = models.ForeignKey(Campaign, blank=True, null=True, related_name="reports", on_delete=models.SET_NULL, help_text="The internal name of the outreach effort.", verbose_name="Outreach Name")
    # If a UTM campaign is provided, but we're not tracking it in the Campaign table, we'll record it here to avoid data loss due to bad configuration.
    unknown_origination_utm_campaign = models.CharField(max_length=700, null=True, blank=True)
    # Identifies search terms.
    origination_utm_term = models.CharField(max_length=100, null=True, blank=True, help_text="Any search terms used in discovering the outreach effort")
    # Identifies what specifically was clicked to bring the user to the site, such as a banner ad or a text link.
    # It is often used for A/B testing and content-targeted ads.
    origination_utm_content = models.CharField(max_length=100, null=True, blank=True, help_text="Identifies what specifically was clicked to bring the user to the site, such as to distinguish between two different outreach links on the same webpage or document.")

    tags = models.ManyToManyField(Tag, blank=True)

    # Metadata
    public_id = models.CharField(max_length=100, null=False, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    crt_reciept_year = models.PositiveIntegerField(MaxValueValidator(datetime.now().year), null=True, blank=True)
    crt_reciept_day = models.PositiveIntegerField(MaxValueValidator(31), null=True, blank=True)
    crt_reciept_month = models.PositiveIntegerField(MaxValueValidator(12), null=True, blank=True)
    intake_format = models.CharField(max_length=100, null=True, default=None, choices=INTAKE_FORMAT_CHOICES)
    author = models.CharField(max_length=1000, null=True, blank=True)
    assigned_to = models.ForeignKey(User, blank=True, null=True, related_name="assigned_complaints", on_delete=models.CASCADE)
    closed_date = models.DateTimeField(blank=True, null=True, help_text="The Date this report's status was most recently set to \"Closed\"")
    language = models.CharField(default='en', max_length=10, blank=True, null=True)
    viewed = models.BooleanField(default=False)
    batched_for_disposal = models.BooleanField(default=False)
    # Eventually, these reports will be deleted - but for now, we can use this
    # boolean to hide them from view.
    disposed = models.BooleanField(default=False)

    # Not in use- but need to preserving historical data
    hatecrimes_trafficking = models.ManyToManyField(HateCrimesandTrafficking, blank=True)

    # referrals
    referred = models.BooleanField(default=False)
    referral_section = models.TextField(choices=SECTION_CHOICES, blank=True)

    litigation_hold = models.BooleanField(default=False)
    retention_schedule = models.ForeignKey(RetentionSchedule, blank=True, null=True, related_name="reports", on_delete=models.SET_NULL)

    violation_summary_search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        indexes = [GinIndex(fields=['violation_summary_search_vector'])]

    def redact(self):
        """Removes all information from the report besides its ID"""

        if self.litigation_hold:
            logger.error(f'Attempted to redact report {self.public_id} while on litigation hold.')
            return

        self.disposed = True

        if not settings.REDACT_REPORTS:
            self.save()
            return

        ignore = [
            'id',
            'public_id',
            'modified_date',
            'retention_schedule',
            'batched_for_disposal',
            'disposed',
            'email_report_count',
        ]

        to_redact = [
            field
            for field in self._meta.get_fields()
            if field.name not in ignore
        ]

        for field in to_redact:
            # Clear out this field, no matter what type it is:

            if field.is_relation:
                if field.one_to_one:
                    getattr(self, field.name).delete()
                    continue

                if field.one_to_many or field.name == 'internal_comments':
                    try:
                        setattr(self, field.name, None)
                    except TypeError:
                        getattr(self, field.name).all().delete()
                    continue

                if field.many_to_many:
                    try:
                        getattr(self, field.name).clear()
                    except FieldDoesNotExist:
                        pass
                    continue

            if field.null:
                setattr(self, field.name, None)
                continue

            if field.blank:
                blank = {
                    fields.CharField: '',
                    fields.TextField: '',
                    fields.IntegerField: 0,
                    fields.BooleanField: False,
                    fields.DateTimeField: datetime.fromtimestamp(0),
                }.get(type(field))
                setattr(self, field.name, blank)
                continue

            if hasattr(field, 'default') and field.default != fields.NOT_PROVIDED:
                setattr(self, field.name, field.default)
                continue

        print(f'Redacted report {self.public_id}')
        self.save()
        return

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
        if self.crt_reciept_year and self.crt_reciept_month and self.crt_reciept_day:
            try:
                return datetime(self.crt_reciept_year, self.crt_reciept_month, self.crt_reciept_day)
            except ValueError:
                return None
        return None

    @cached_property
    def summary(self):
        """Finds the summary from the report's internal comments list.

        This should be preferred when prefetch_related has been used.

        Avoid this when data has not been prefetched -  django ORM query would be better.
        """
        summaries = sorted([
            summary
            for summary
            in self.internal_comments.all()
            if summary.is_summary
        ], key=lambda s: s.modified_date, reverse=True)

        if not summaries:
            return None

        return summaries[0]

    def __str__(self):
        return self.public_id

    immigration_classes = {
        'immigration',
        'national_origin',
        'language'
    }

    disability_classes = {
        'disability'
    }

    def assign_section(self):
        """See the SectionAssignmentTests for expected behaviors"""
        protected_classes = {pc.value for pc in self.protected_class.all()}
        is_disabled = bool(self.disability_classes & protected_classes)
        is_only_immigration = bool(protected_classes - self.immigration_classes)

        if self.primary_complaint == 'voting':
            if is_disabled:
                return 'DRS'
            return 'VOT'

        if self.primary_complaint == 'workplace':
            if not protected_classes:
                return 'ELS'
            if is_only_immigration:
                return 'ELS'
            return 'IER'

        if self.primary_complaint == 'commercial_or_public':
            if is_disabled:
                return 'DRS'
            if self.commercial_or_public_place == 'healthcare':
                return 'SPL'
            return 'HCE'

        if self.primary_complaint == 'housing':
            return 'HCE'

        if self.primary_complaint == 'education':
            if self.public_or_private_school == 'public' or self.public_or_private_school == 'not_sure':
                return 'EOS'
            if is_disabled:
                return 'DRS'
            return 'EOS'

        if self.primary_complaint == 'police':
            if is_disabled:
                return 'DRS'
            if self.inside_correctional_facility == 'inside':
                return 'SPL'
            return 'CRM'

        if self.primary_complaint == 'something_else' and is_disabled:
            return 'DRS'

        return 'ADM'

    def assign_district(self):
        if not self.location_city_town:
            return None
        if not self.location_state:
            return None

        city = sanitize.sanitize_city(self.location_city_town)
        state = self.location_state
        district_query = JudicialDistrict.objects.filter(city=city, state=state)
        if len(district_query) <= 0:
            return None

        return district_query[0].district

    @property
    def get_summary(self):
        """Return most recent summary provided by an intake specialist"""
        return self.internal_comments.filter(is_summary=True).order_by('-modified_date').first()

    @property
    def addressee(self):
        if self.contact_full_name:
            return f"Dear {self.contact_full_name}"
        return "Thank you for your report"

    @property
    def addressee_es(self):
        if self.contact_full_name:
            return f"Estimado/a {self.contact_full_name}"
        return "Gracias por su informe"

    @property
    def addressee_ko(self):
        if self.contact_full_name:
            return f"{self.contact_full_name}님께"
        return "신고해 주셔서 감사합니다"

    @property
    def addressee_tl(self):
        if self.contact_full_name:
            return f"Mahal na {self.contact_full_name}"
        return "Salamat sa iyong ulat"

    @property
    def addressee_vi(self):
        if self.contact_full_name:
            return f"Kính gửi {self.contact_full_name}"
        return "Cảm ơn quý vị đã báo cáo"

    @property
    def addressee_zh_hans(self):
        if self.contact_full_name:
            return f"{self.contact_full_name}您好"
        return "感谢您的报告"

    @property
    def addressee_zh_hant(self):
        if self.contact_full_name:
            return f"{self.contact_full_name}您好"
        return "感謝您提交報告"

    def get_absolute_url(self):
        return reverse('crt_forms:crt-forms-show', kwargs={"id": self.id})

    @property
    def closed(self):
        return self.status == CLOSED_STATUS

    def activity(self):
        return self.target_actions.exclude(verb__contains='comment:').prefetch_related('actor')

    def closeout_report(self):
        """
        Remove assignee and record date of call
        """
        self.assigned_to = None
        local_tz = pytz.timezone('US/Eastern')
        self.closed_date = datetime.now(local_tz)

    def reset_for_changed_section(self):
        """
        Remove assignee and update status to new
        """
        self.assigned_to = None
        self.status = 'new'
        self.primary_statute = None
        self.retention_schedule = None
        self.referred = False
        self.dj_number = None
        self.district = None

    @cached_property
    def related_reports(self):
        """Return qs of reports with the same value for `contact_email`"""
        return Report.objects.exclude(contact_email__isnull=True).filter(contact_email__iexact=self.contact_email).order_by('status', '-create_date')[:1000]

    @cached_property
    def email_responses(self):
        """Populate data showing responses we've sent and their status."""
        return list(self.emails.exclude(purpose='internal').order_by('-created_at').values(
            'completed_at',
            'created_at',
            'error_message',
            'purpose',
            'status',
            'tms_id',
        ))

    @cached_property
    def related_reports_display(self):
        """Return set of related reports grouped by STATUS for template rendering"""
        reports = self.related_reports
        display = {'new': [], 'open': [], 'closed': []}
        for report in reports:
            display[report.status].append(report)

        return (('new', display['new']),
                ('open', display['open']),
                ('closed', display['closed']),
                )

    @cached_property
    def recent_email_sent(self):
        """Returns the name of the last email template sent in response to this report"""
        recent_contact_activity = self.activity().filter(verb='Contacted complainant:', description__contains='Email sent').first()
        if recent_contact_activity:
            try:
                email = recent_contact_activity.description.split("'")[1]
            except IndexError:
                email = None
            return email
        return None

    @property
    def contact_full_name(self):
        """
        Return full name if both first and last are present
        otherwise return whichever value is present
        If both are missing, return an empty string
        """
        first = self.contact_first_name
        last = self.contact_last_name
        if first and last:
            return f'{first} {last}'
        return first or last


class ReportDispositionBatch(models.Model):
    """A group of reports that have been disposed of together."""
    class Meta:
        permissions = (
            ("review_dispositionbatch", "Can approve or reject disposition batches"),
        )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    disposed_date = models.DateTimeField(auto_now_add=True)
    create_date = models.DateTimeField(blank=True, null=True)
    proposed_disposal_date = models.DateTimeField(blank=True, null=True)
    disposed_by = models.ForeignKey(User, related_name="disposed_report_batches", on_delete=models.PROTECT, blank=True, null=True, help_text="Intake specialist who created batch.")
    disposed_count = models.IntegerField(default=0)
    status = models.TextField(choices=BATCH_STATUS_CHOICES, default='ready')
    first_reviewer = models.ForeignKey(User, related_name="reviewed_disposed_report_batch", blank=True, null=True, on_delete=models.PROTECT, help_text="First records team reviewer.")
    first_review_date = models.DateTimeField(blank=True, null=True, help_text="Date of the first records team review.")
    second_reviewer = models.ForeignKey(User, related_name="second_reviewed_disposed_report_batch", blank=True, null=True, on_delete=models.PROTECT, help_text="Second records team reviewer.")
    second_review_date = models.DateTimeField(blank=True, null=True, help_text="Date of the second records team review.")
    notes = models.TextField(max_length=7000, null=True, blank=True, help_text="Internal notes about batch from the first reviewer.")
    second_review_notes = models.TextField(max_length=7000, null=True, blank=True, help_text="Internal notes about batch from the second reviewer.")

    def add_records_to_batch(self, queryset, user):
        """Creates a batch of disposed reports."""
        if not user:
            raise ValueError("Cannot determine the current user for report disposal.")
        # Creating a new queryset by filtering by id so we can update the
        # batched_for_disposal field after limiting the record number to 500
        ids = queryset.values_list('pk', flat=True)
        queryset = Report.objects.filter(pk__in=list(ids))
        queryset.update(batched_for_disposal=True)
        ReportDisposition.objects.bulk_create([
            ReportDisposition(
                schedule=report.retention_schedule,
                batch=self,
                public_id=report.public_id)
            for report
            in queryset.all().only('retention_schedule', 'public_id')
        ])

    def redact_reports(self):
        """Deletes (blanks out) all reports in the batch."""
        public_ids = self.disposed_reports.values_list('public_id', flat=True)
        reports = Report.objects.filter(public_id__in=public_ids).all()

        for report in reports:
            report.redact()

    @classmethod
    def dispose(cls, queryset):
        """Creates a batch of disposed reports."""
        current_request = CrequestMiddleware.get_request()
        if not current_request:
            raise ValueError("Cannot determine the current user for report disposal.")

        user = current_request.user
        if not user:
            raise ValueError("Cannot determine the current user for report disposal.")

        with transaction.atomic():
            batch = cls.objects.create(disposed_by=user,
                                       disposed_count=queryset.count())
            ReportDisposition.objects.bulk_create([
                ReportDisposition(
                    schedule=report.retention_schedule,
                    batch=batch,
                    public_id=report.public_id)
                for report
                in queryset.all().select_related('retention_schedule').only('retention_schedule', 'public_id')
            ])

        return batch


class ReportDisposition(models.Model):
    """Records the deletion of a report in accordance with a retention schedule."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    schedule = models.ForeignKey(RetentionSchedule, related_name="disposed_reports", on_delete=models.PROTECT)
    batch = models.ForeignKey(ReportDispositionBatch, related_name="disposed_reports", on_delete=models.PROTECT)
    public_id = models.CharField(max_length=100, null=False, blank=False, help_text="The record locator for the disposed report")
    rejected = models.BooleanField(default=False)


class ReportAttachment(models.Model):
    file = models.FileField(upload_to='attachments', validators=[validate_file_attachment])
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    report = models.ForeignKey(Report, blank=True, null=True, on_delete=models.SET_NULL, related_name='attachments')
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('crt_forms:get-report-attachment', kwargs={"id": self.report.id, "attachment_id": self.id})


class ReportsData(models.Model):
    file = models.FileField(upload_to='report-data')
    filename = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('crt_forms:get-report-data', kwargs={"report_data_id": self.id})


class AddConfigurableContentMigration(migrations.RunPython):
    def __init__(self, machine_name, *, content='This is placeholder content', **kwargs):
        if '_' in machine_name:
            raise ValueError('Underscores are not allowed in machine names. Use dashes instead.')

        def add_configurable_content(apps, schema_editor):
            drop_configurable_content(apps, schema_editor)
            ConfigurableContent.objects.create(machine_name=machine_name, content=content)

        def drop_configurable_content(apps, schema_editor):
            del apps, schema_editor  # unused
            try:
                ConfigurableContent.objects.get(machine_name=machine_name).delete()
            except ConfigurableContent.DoesNotExist:
                pass

        super().__init__(add_configurable_content, drop_configurable_content, **kwargs)


class ConfigurableContent(models.Model):
    machine_name = models.CharField(max_length=500, null=False, unique=True, blank=False, help_text="A short, non-changing name to be used in template code.")
    content = models.TextField(null=False, blank=True, help_text="The content to display in the template.")

    def render(self, optionals=None, extensions=None, **kwargs):
        return markdown.markdown(self.content, extensions=['extra', 'sane_lists', 'admonition', 'nl2br'])


class RepeatWriterInfo(models.Model):
    # We might consider adding these in the future to have a one stop shop to check for Repeat writers
    # contact_first_name = models.CharField(max_length=225, null=True, blank=True)
    # contact_last_name = models.CharField(max_length=225, null=True, blank=True)
    # repeat_writer_form_sent = models.BooleanField(default=False)
    email = models.EmailField(unique=True, primary_key=True, help_text="Email associated with number of reports")
    count = models.IntegerField()

    class Meta:
        """This model is tied to a view created from migration 93"""
        managed = False
        db_table = 'repeat_writer_view'

    @staticmethod
    def refresh_view():
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW repeat_writer_view;")
        end = time.time()
        elapsed = round(end - start, 4)
        logger.info(f'SUCCESS: Refreshed Email view in {elapsed} seconds')


class EmailReportCount(models.Model):
    """see the total number of reports that are associated with the contact_email for each report"""
    report = models.OneToOneField(Report, primary_key=True, on_delete=models.CASCADE, related_name='email_report_count')
    email_count = models.IntegerField()

    class Meta:
        """This model is tied to a view created from migration 93"""
        managed = False
        db_table = 'email_report_count'

    @staticmethod
    def refresh_view():
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY email_report_count;")
        end = time.time()
        elapsed = round(end - start, 4)
        logger.info(f'SUCCESS: Refreshed Email view in {elapsed} seconds')


class Trends(models.Model):
    """see the top 10 non-stop words from violation summary """
    word = models.TextField()
    document_count = models.IntegerField()
    word_count = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    record_type = models.TextField()

    class Meta:
        """This model is tied to a view created from migration 73"""
        managed = False
        db_table = 'trends'

    @staticmethod
    def refresh_view():
        logger.info("Refreshing Trends view...")
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW trends;")
        logger.info("Trends view refreshed")


class FormLettersSent(models.Model):
    """see the number of actions taken per section"""
    report_id = models.IntegerField(primary_key=True)
    assigned_section = models.TextField()
    timestamp = models.DateTimeField()
    description = models.TextField()

    class Meta:
        """This model is tied to a view created from migration 144"""
        managed = False
        db_table = "form_letters_sent"

    @staticmethod
    def refresh_view():
        logger.info("Refreshing Form Letters Sent view....")
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW form_letters_sent;")
        logger.info("FormLetter Sent view refreshed")


class ResponseTemplate(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False, unique=True,)
    subject = models.CharField(max_length=150, null=False, blank=False,)
    body = models.TextField(null=False, blank=False,)
    language = models.CharField(default='en', max_length=10, null=False, blank=False,)
    is_html = models.BooleanField('HTML email', default=False,)
    show_in_dropdown = models.BooleanField('Show in select template dropdown', default=True,)
    is_notification = models.BooleanField('Only for use by notification systems', default=False,)
    is_user_created = models.BooleanField('Is user created', default=True,)
    referral_contact = models.ForeignKey(ReferralContact, blank=True, null=True, related_name="response_templates", on_delete=models.SET_NULL)

    optionals = None

    def utc_timezone_to_est(self, utc_dt):
        local_tz = pytz.timezone('US/Eastern')
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)

    def get_optionals(self):
        return get_optionals(self.body)

    def available_report_fields(self, report: Optional[Report]):
        """
        Only permit a small subset of report fields
        """
        today = datetime.today()
        section_choices = dict(SECTION_CHOICES)
        section_choices_es = dict(SECTION_CHOICES_ES)
        section_choices_ko = dict(SECTION_CHOICES_KO)
        section_choices_tl = dict(SECTION_CHOICES_TL)
        section_choices_vi = dict(SECTION_CHOICES_VI)
        section_choices_zh_hans = dict(SECTION_CHOICES_ZH_HANS)
        section_choices_zh_hant = dict(SECTION_CHOICES_ZH_HANT)

        if not report:
            return Context({
                'outgoing_date': format_date(today, locale='en_US'),
            })

        # For ProForm reports, the date the report was received is more relevant than the create date, so
        # we use that when it is available
        try:
            if report.crt_reciept_date and report.intake_format != 'web':
                report_create_date_est = report.crt_reciept_date
            else:
                report_create_date_est = self.utc_timezone_to_est(report.create_date)
        except ValueError:
            report_create_date_est = self.utc_timezone_to_est(report.create_date)

        referral_text = ''
        if self.referral_contact:
            referral_translations = self.referral_contact.variable_text or {}
            referral_en = referral_translations.get('en')
            referral_translated = referral_translations.get(self.language)
            referral_text = referral_translated or referral_en or ''

        return Context({
            'record_locator': report.public_id,
            'addressee': report.addressee,
            'complainant_name': f'{report.contact_first_name} {report.contact_last_name}',
            'organization_name': report.location_name,
            'date_of_intake': format_date(report_create_date_est, format='long', locale='en_US'),
            'outgoing_date': format_date(today, locale='en_US'),  # required for paper mail
            'section_name': section_choices.get(report.assigned_section, "no section"),
            'referral_text': referral_text,
            # spanish translations
            'es': {
                'addressee': report.addressee_es,
                'date_of_intake': format_date(report_create_date_est, format='long', locale='es_ES'),
                'outgoing_date': format_date(today, locale='es_ES'),
                'section_name': section_choices_es.get(report.assigned_section, "no section"),
            },
            'ko': {
                'addressee': report.addressee_ko,
                'date_of_intake': format_date(report_create_date_est, format='long', locale='ko'),
                'outgoing_date': format_date(today, locale='ko'),
                'section_name': section_choices_ko.get(report.assigned_section, "no section"),
            },
            'tl': {
                'addressee': report.addressee_tl,
                'date_of_intake': format_date(report_create_date_est, format='long', locale='tl'),
                'outgoing_date': format_date(today, locale='tl'),
                'section_name': section_choices_tl.get(report.assigned_section, "no section"),
            },
            'vi': {
                'addressee': report.addressee_vi,
                'date_of_intake': format_date(report_create_date_est, format='long', locale='vi'),
                'outgoing_date': format_date(today, locale='vi'),
                'section_name': section_choices_vi.get(report.assigned_section, "no section"),
            },
            'zh_hans': {
                'addressee': report.addressee_zh_hans,
                'date_of_intake': format_date(report_create_date_est, format='long', locale='zh_hans'),
                'outgoing_date': format_date(today, locale='zh_hans'),
                'section_name': section_choices_zh_hans.get(report.assigned_section, "no section"),
            },
            'zh_hant': {
                'addressee': report.addressee_zh_hant,
                'date_of_intake': format_date(report_create_date_est, format='long', locale='zh_hant'),
                'outgoing_date': format_date(today, locale='zh_hant'),
                'section_name': section_choices_zh_hant.get(report.assigned_section, "no section"),
            },
        })

    def render_subject(self, report, **kwargs):
        template = Template(self.subject)
        context = self.available_report_fields(report)
        context.update({**kwargs, 'report': report})
        return escape(template.render(context))

    def render_body_as_markdown(self, report, optionals=None, extensions=None, **kwargs):
        if extensions is None:
            extensions = []
        if optionals is None:
            optionals = self.optionals
        template = Template(self.body)
        context = self.available_report_fields(report)
        context.update({**kwargs, 'report': report})
        rendered = template.render(context)
        if self.is_html:
            return markdown.markdown(rendered, extensions=[OptionalExtension(include=optionals), 'extra', 'sane_lists', 'admonition', 'nl2br', *extensions])
        return rendered.replace('\n', '<br>')

    def render_body(self, report, **kwargs):
        template = Template(self.body)
        context = self.available_report_fields(report)
        context.update({**kwargs, 'report': report})
        return escape(template.render(context))

    def render_plaintext(self, report, optionals=None, **kwargs):
        if optionals is None:
            optionals = self.optionals
        template = Template(self.body)
        context = self.available_report_fields(report)
        context.update({**kwargs, 'report': report})
        rendered = template.render(context)
        optional_processor = OptionalProcessor(include=self.optionals)
        return escape('\n'.join(optional_processor.run(rendered.split('\n'))))

    def render_bulk_subject(self, report, reports, **kwargs):
        template = Template(self.subject)
        context = self.available_report_fields(report)
        context.update({**kwargs, 'report': report, 'reports': reports})
        return escape(template.render(context))

    def render_bulk_body(self, report, reports, **kwargs):
        template = Template(self.body)
        context = self.available_report_fields(report)
        context.update({**kwargs, 'report': report, 'reports': reports})
        return escape(template.render(context))

    def __str__(self):
        return self.title


class DoNotEmail(models.Model):
    """
    Email addresses which, if present, have been flagged as one to which
    we will no longer attempt to deliver email messages
    """
    recipient = models.EmailField(unique=True, help_text="Emails will not be sent to the address added here")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Do Not Email recipient'

    def __str__(self):
        return self.recipient


class ResourceContact(models.Model):
    """
    Organized resources to share with public users.
    """
    first_name = models.CharField(max_length=225, null=True, blank=True)
    last_name = models.CharField(max_length=225, null=True, blank=True)
    title = models.CharField(max_length=225, null=True, blank=True)
    email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )


class Resource(models.Model):
    """
    Organized resources to share with public users.
    """
    name = models.CharField(max_length=255, null=False, blank=False, help_text="The name of the resource as it will appear in lists and dropdowns.")
    section = models.TextField(choices=SECTION_CHOICES, null=True, blank=True, default=None, help_text="The section to which this resource applies.")
    url = models.TextField(null=True, blank=True, help_text="Address of resource website.")
    email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    secondary_email = models.CharField(max_length=225, null=True, blank=True, validators=[validate_email_address])
    phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )
    secondary_phone = models.CharField(
        validators=[RegexValidator(phone_validation_regex, message=CONTACT_PHONE_INVALID_MESSAGE)],
        max_length=225,
        null=True,
        blank=True
    )
    contacts = models.ManyToManyField(ResourceContact, blank=True)
    notes = models.TextField(max_length=7000, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    outreach_efforts = models.TextField(max_length=1000, null=True, blank=True)
    background = models.TextField(max_length=1000, null=True, blank=True)
    soi_opportunities = models.BooleanField(default=False, null=False)
    need_followup = models.BooleanField(default=False, null=False)
