"""All models need to be added to signals.py for proper logging."""
import logging
from datetime import datetime
from babel.dates import format_date

from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import connection, models
from django.template import Context, Template
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import escape

from .managers import ActiveProtectedClassChoiceManager
from .model_variables import (CLOSED_STATUS,
                              COMMERCIAL_OR_PUBLIC_PLACE_CHOICES,
                              CONTACT_PHONE_INVALID_MESSAGE,
                              CORRECTIONAL_FACILITY_LOCATION_CHOICES,
                              CORRECTIONAL_FACILITY_LOCATION_TYPE_CHOICES,
                              DATE_ERRORS, DISTRICT_CHOICES, ELECTION_CHOICES,
                              EMPLOYER_SIZE_CHOICES, HATE_CRIME_CHOICES,
                              HATE_CRIMES_TRAFFICKING_MODEL_CHOICES,
                              INTAKE_FORMAT_CHOICES, PRIMARY_COMPLAINT_CHOICES,
                              PROTECTED_MODEL_CHOICES,
                              PUBLIC_OR_PRIVATE_EMPLOYER_CHOICES,
                              PUBLIC_OR_PRIVATE_SCHOOL_CHOICES,
                              SECTION_CHOICES, SECTION_CHOICES_ES,
                              SECTION_CHOICES_KO,
                              SECTION_CHOICES_TL,
                              SECTION_CHOICES_VI,
                              SECTION_CHOICES_ZH_HANS,
                              SECTION_CHOICES_ZH_HANT,
                              SERVICEMEMBER_CHOICES,
                              STATES_AND_TERRITORIES, STATUS_CHOICES,
                              STATUTE_CHOICES)
from .phone_regex import phone_validation_regex
import pytz
from .validators import validate_file_attachment, validate_email_address

logger = logging.getLogger(__name__)
User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    intake_filters = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return str(self.user)


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


class Report(models.Model):
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

    servicemember = models.CharField(max_length=4, null=True, blank=True, choices=SERVICEMEMBER_CHOICES)

    # Primary Issue
    primary_complaint = models.CharField(
        max_length=100,
        choices=PRIMARY_COMPLAINT_CHOICES,
        default='',
        blank=False
    )

    hate_crime = models.CharField(max_length=4, null=True, blank=True, choices=HATE_CRIME_CHOICES)

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
    opened = models.BooleanField(default=False)

    # Not in use- but need to preserving historical data
    hatecrimes_trafficking = models.ManyToManyField(HateCrimesandTrafficking, blank=True)

    # referrals
    referred = models.BooleanField(default=False)
    referral_section = models.TextField(choices=SECTION_CHOICES, blank=True)

    violation_summary_search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        indexes = [GinIndex(fields=['violation_summary_search_vector'])]

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
        return self.public_id

    def __has_immigration_protected_classes(self, pcs):
        immigration_classes = [
            'immigration',
            'national_origin',
            'language'
        ]
        is_not_included = set(pcs).isdisjoint(set(immigration_classes))

        if is_not_included:
            return False

        return True

    def __is_not_disabled(self, pcs):
        return 'disability' not in pcs

    def assign_section(self):
        """See the SectionAssignmentTests for expected behaviors"""
        protected_classes = [pc.value for pc in self.protected_class.all()]

        if self.primary_complaint == 'voting':
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
            elif self.public_or_private_school == 'private' and not self.__is_not_disabled(protected_classes):
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
        self.closed_date = datetime.now()

    def status_assignee_reset(self):
        """
        Remove assignee and update status to new
        """
        self.assigned_to = None
        self.status = 'new'

    @cached_property
    def related_reports(self):
        """Return qs of reports with the same value for `contact_email`"""
        return Report.objects.exclude(contact_email__isnull=True).filter(contact_email__iexact=self.contact_email).order_by('status', '-create_date')

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


class ReportAttachment(models.Model):
    file = models.FileField(upload_to='attachments', validators=[validate_file_attachment])
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='attachments')
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('crt_forms:get-report-attachment', kwargs={"id": self.report.id, "attachment_id": self.id})


class EmailReportCount(models.Model):
    """see the total number of reports that are associated with the contact_email for each report"""
    report = models.OneToOneField(Report, primary_key=True, on_delete=models.CASCADE, related_name='email_report_count')
    email_count = models.IntegerField()

    class Meta:
        """This model is tied to a view created from migration 93"""
        managed = False
        db_table = 'email_report_count'


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


class ResponseTemplate(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False, unique=True,)
    subject = models.CharField(max_length=150, null=False, blank=False,)
    body = models.TextField(null=False, blank=False,)
    language = models.CharField(default='en', max_length=10, null=False, blank=False,)

    def utc_timezone_to_est(self, utc_dt):
        local_tz = pytz.timezone('US/Eastern')
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)

    def available_report_fields(self, report):
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

        # as of July 1, create_dates are being converted to eastern standard time from utc
        # to show the correct date for reports created in the evening.
        report_create_date_est = self.utc_timezone_to_est(report.create_date)

        return Context({
            'record_locator': report.public_id,
            'addressee': report.addressee,
            'date_of_intake': format_date(report_create_date_est, format='long', locale='en_US'),
            'outgoing_date': format_date(today, locale='en_US'),  # required for paper mail
            'section_name': section_choices.get(report.assigned_section, "no section"),
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

    def render_subject(self, report):
        template = Template(self.subject)
        context = self.available_report_fields(report)
        return escape(template.render(context))

    def render_body(self, report):
        template = Template(self.body)
        context = self.available_report_fields(report)
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
