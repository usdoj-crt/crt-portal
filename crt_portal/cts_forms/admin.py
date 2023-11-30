import csv
import io
import logging
import zipfile

from actstream.models import Action, Follow
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import StringAgg
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpRequest
from django.core.paginator import Paginator
from django.db.models import Subquery, OuterRef
from django import forms
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.urls import reverse, path
from django.db.models.functions import Lower

from utils import pdf
from .filters import get_report_filter_from_search

from .model_variables import SECTION_CHOICES

from .models import (CommentAndSummary, HateCrimesandTrafficking, Profile,
                     ProtectedClass, Report, ResponseTemplate, DoNotEmail,
                     JudicialDistrict, RetentionSchedule, RoutingSection, RoutingStepOneContact,
                     VotingMode, Campaign, ReferralContact, BannerMessage, SavedSearch, NotificationPreference)
from .signals import get_client_ip

logger = logging.getLogger(__name__)

EXCLUDED_REPORT_FIELDS = ['violation_summary_search_vector']
REPORT_FIELDS = [field.name for field in Report._meta.fields if field.name not in EXCLUDED_REPORT_FIELDS]
ACTION_FIELDS = ['timestamp', 'actor', 'verb', 'description', 'target']


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """Disable add, modify, and delete functionality"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


class TranslatedTextWidget(AdminTextareaWidget):
    """Shows an entry for each language in settings.LANGUAGES."""

    def __init__(self, attrs=None):
        codes = ','.join([code for code, name in settings.LANGUAGES])
        super().__init__(attrs={
            'class': 'vTranslatedTextField',
            'data-language-codes': codes,
            **(attrs or {})
        })

    media = forms.Media(js=['js/translated_text_widget.js'])


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def format_export_message(request, records, what_was_exported):
    """Log user and # of records exported"""
    ip = get_client_ip(request) if request else 'CLI'
    username = request.user.username if request else 'CLI'
    userid = request.user.id if request else 'CLI'
    return f'ADMIN ACTION by: {username} {userid} @ {ip}. Exported {records} {what_was_exported} as csv.'


def iter_queryset(queryset, headers, *, pagination=settings.DEFAULT_EXPORT_PAGINATION):
    """
    The iterator provided by queryset.iterator isn't adequate here

    We add headers to our output

    We also need to traverse M2M relationships for at least 1 field
    and want tos use prefetch_related to avoid a query for each instance
    queryset.iterator ignores `prefetch_related` so instead we paginate
    through the queryset to reduce the number of total queries required
    """
    yield headers
    paginator = Paginator(queryset, pagination)
    for i in range(paginator.num_pages):
        yield from paginator.get_page(i + 1)


def prepare_report_csv_queryset(queryset):
    """
    Customize the rendering of protected_class and summary instances
    while rendering headers as-is
    """

    summaries = (
        CommentAndSummary.objects
        .filter(is_summary=True, report=OuterRef('pk'))
        .order_by('-modified_date')
        .only('note')
    )

    return (
        queryset
        .prefetch_related('protected_class')
        .annotate(_exportable_protected_class=StringAgg('protected_class__protected_class', delimiter='; '))
        .annotate(_exportable_summary=Subquery(summaries.values('note')[:1]))
        .order_by('id')
        .values_list(*REPORT_FIELDS,
                     '_exportable_protected_class',
                     '_exportable_summary')
    )


def _serialize_action(data):
    """Preserve headers while rendering ACTION_FIELDS for inbound actions"""
    if isinstance(data, Action):
        return [getattr(data, field) for field in ACTION_FIELDS]
    return data


def export_reports_as_csv(modeladmin, request, queryset):
    """
    Stream all non-related fields,
    protected_class M2M,
    and latest summary from CommentAndSummary M2M of selected reports as a CSV
    Log all use
    """
    writer = csv.writer(Echo(), quoting=csv.QUOTE_ALL)
    headers = REPORT_FIELDS + ['protected_class', 'internal_summary']

    iterator = iter_queryset(prepare_report_csv_queryset(queryset), headers)

    response = StreamingHttpResponse((writer.writerow(report) for report in iterator),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="report_export.csv"'

    logger.info(format_export_message(request, queryset.count(), 'reports'))
    return response


export_reports_as_csv.allowed_permissions = ('view',)  # noqa


def export_actions_as_csv(modeladmin, request, queryset):
    """
    Stream actions as csv
    Log all use
    """
    writer = csv.writer(Echo(), quoting=csv.QUOTE_ALL)
    iterator = iter_queryset(queryset, ACTION_FIELDS)

    response = StreamingHttpResponse((writer.writerow(_serialize_action(action)) for action in iterator),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="activity_export.csv"'

    logger.info(format_export_message(request, queryset.count(), 'activity log entries'))
    return response


export_actions_as_csv.allowed_permissions = ('view',)  # noqa


def export_reports_as_pdf(modeladmin, request, queryset):
    """Export a zip file containing Reports as pdf files."""
    del modeladmin, request  # Unused
    buffer = io.BytesIO()
    archive = zipfile.ZipFile(buffer, "w")

    if queryset.count() == 1:
        try:
            content = pdf.convert_report_to_pdf(queryset.first())
            return HttpResponse(content.getvalue(), content_type="application/pdf")
        except pdf.FailedToGeneratePDF as error:
            logging.exception(error)
            return HttpResponse(f'{error}', status=500)

    errors = []
    for report in queryset:
        try:
            content = pdf.convert_report_to_pdf(report)
            archive.writestr(f'{report.public_id}.pdf', content.getvalue())
        except pdf.FailedToGeneratePDF as error:
            logging.exception(error)
            errors.append(f'{report.public_id}: {error}')
    if errors:
        archive.writestr("errors.txt", "\n".join(errors))
    archive.close()

    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="reports_export.zip"'

    return response


export_reports_as_pdf.allowed_permissions = ('view',)  # noqa


class ReportAdmin(ReadOnlyModelAdmin):
    """
    View-only report admin providing filtering and export functionality
    """
    list_display = ['public_id', 'status', 'assigned_section', 'create_date', 'modified_date', 'assigned_to']
    list_filter = [
        'status',
        'viewed',
        'create_date',
        'modified_date',
        'assigned_section',
        'servicemember',
        'hate_crime',
        'primary_complaint',
        'assigned_to',
        'origination_utm_campaign',
    ]
    ordering = ['public_id']
    actions = [export_reports_as_csv, export_reports_as_pdf]


class ActorActionFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'actor'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'actor_object_id'

    def lookups(self, request, model_admin):
        users = [u for u in User.objects.all().order_by(Lower('username'))]
        return [(user.id, user.username) for user in users]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if not self.value():
            return queryset
        else:
            return queryset.filter(actor_object_id=self.value())


class ActionAdmin(ReadOnlyModelAdmin):
    """Read-only admin for browsing and exporting raw activity log entries"""
    search_fields = ['description']
    date_hierarchy = 'timestamp'
    list_display = ('timestamp', 'actor', 'verb', 'description', 'target')
    list_editable = ('verb',)
    list_filter = ('timestamp', 'verb', ActorActionFilter)
    raw_id_fields = ('actor_content_type', 'target_content_type',
                     'action_object_content_type')
    actions = [export_actions_as_csv]


class JudicialDistrictAdmin(ReadOnlyModelAdmin):
    list_display = ['zipcode', 'city', 'county', 'state', 'district']
    list_filter = ['district']
    search_fields = ['zipcode', 'city', 'county', 'state', 'district']


class RoutingSectionAdmin(admin.ModelAdmin):
    list_display = ['section', 'names']


class RoutingStepOneContactAdmin(admin.ModelAdmin):
    list_display = ['contacts']


class VotingModeAdmin(admin.ModelAdmin):
    list_display = ['voting_toggle_display_name']

    @admin.display(description='Voting Toggle')
    def voting_toggle_display_name(self, obj):
        if obj.toggle:
            return 'Voting Mode: True'
        return 'Voting Mode: False'


class ReferralContactAdminForm(forms.ModelForm):
    class Meta:
        model = ReferralContact
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['variable_text'].widget = TranslatedTextWidget()


class ReferralContactAdmin(admin.ModelAdmin):
    list_display = ['machine_name', 'name', 'notes', 'show_as_referral']
    form = ReferralContactAdminForm


class BannerMessageAdminForm(forms.ModelForm):
    class Meta:
        model = BannerMessage
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['markdown_content'].widget = TranslatedTextWidget()


class BannerMessageAdmin(admin.ModelAdmin):
    def get_ordering(self, request):
        return ['order']

    list_display = ['order', 'show', 'kind', 'english']
    form = BannerMessageAdminForm


def mark_as_archived(modeladmin, request, queryset):
    queryset.update(archived=True)


def unmark_as_archived(modeladmin, request, queryset):
    queryset.update(archived=False)


mark_as_archived.allowed_permissions = ('change',)  # noqa
unmark_as_archived.allowed_permissions = ('change',)  # noqa


class CampaignAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'js/admin_copy.js',
            'js/absolute_url.js',
        )
        css = {
            'all': ('css/compiled/admin.css',)
        }

    list_display = ['uuid', 'section', 'internal_name', 'archived', 'shorten_url', 'campaign_url']
    readonly_fields = ['campaign_url', 'shorten_url']
    actions = [mark_as_archived, unmark_as_archived]

    @admin.display(description='Short URL')
    def shorten_url(self, obj):
        # Find ShortenedURL objects containing the campaign uuid
        ShortenedURL = apps.get_model('shortener', 'ShortenedURL')
        short = ShortenedURL.objects.filter(destination=obj.get_absolute_url()).first()
        if not short:
            return self._get_create_short_link(obj)

        admin_edit = reverse('admin:shortener_shortenedurl_change', args=[short.pk])
        short_url = short.get_short_url()

        copy = f'<input aria-label="Short URL" disabled="disabled" class="admin-copy absolute-url" value="{short_url}"/>'
        edit = f'<a class="button" href="{admin_edit}">Change Short URL</a>'
        return mark_safe(f'<div>{copy} {edit}</div>')

    def _get_create_short_link(self, obj):
        url = obj.get_absolute_url()
        name = obj.internal_name.lower().replace(' ', '-')
        add_short_link = reverse('admin:shortener_shortenedurl_add') + f'?destination={url}&shortname={name}'
        return mark_safe(f'<a class="button" href="{add_short_link}">Create Short URL</a>')

    @admin.display(description='Long URL')
    def campaign_url(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f'<input aria-label="Long URL" disabled="disabled" class="admin-copy absolute-url" value="{url}"/>')


def export_templates_as_zip(modeladmin, request, queryset):
    """Export a zip file containing all of the database's response templates."""
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, "w")

    for template in queryset:
        filename = slugify(template.title) + ".md"
        zip_file.writestr(filename, template.body)

    zip_file.close()

    response = HttpResponse(buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="templates.zip"'

    return response


export_templates_as_zip.allowed_permissions = ('view',)  # noqa


class RetentionScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'da_number', 'is_retired', 'order', 'tooltip']
    search_fields = ['name', 'da_number']
    ordering = ['order']


class ResponseTemplateAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/response_template_preview.js',)
        css = {
            'all': ('css/compiled/admin.css',)
        }

    actions = [export_templates_as_zip]
    exclude = ['is_user_created']
    readonly_fields = ['template_help', 'print_template', 'preview']

    @admin.display(description='Template Help')
    def template_help(self, obj):
        return mark_safe('For help with template variables and formatting, <a target="_blank" href="/api/preview-response">go here</a>')

    @admin.display(description='Print Email Preview')
    def print_template(self, obj):
        return mark_safe('<button class="button" id="print_template_preview">Print Email Preview</button>')

    @admin.display(description='Email Preview')
    def preview(self, obj):
        return mark_safe('<iframe class="response-template-preview"'
                         'width="100%" height="100%"'
                         '></iframe>')


class SavedSearchAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'js/admin_copy.js',
            'js/absolute_url.js',
        )
        css = {
            'all': ('css/compiled/admin.css',)
        }

    list_display = ['id', 'name', 'query']
    readonly_fields = ['search_url', 'matching_reports']

    @admin.display(description='Search Results')
    def search_url(self, obj):
        url = obj.get_absolute_url()
        return mark_safe(f'<input aria-label="Search Results" disabled="disabled" class="admin-copy absolute-url" value="{url}"/>')

    @admin.display(description='Matching Reports')
    def matching_reports(self, obj):
        try:
            reports, _ = get_report_filter_from_search(obj)
            count = reports.count()
        except Exception as e:
            return f'Something went wrong running this search: {e}'
        url = obj.get_absolute_url()
        return mark_safe(f'<a href="{url}">View {count} matching reports</a>')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class NotificationPreferenceInline(admin.StackedInline):
    model = NotificationPreference
    can_delete = True
    verbose_name_plural = 'Notification Preferences'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, NotificationPreferenceInline)
    actions = ("bulk_change_profile", *UserAdmin.actions)

    list_filter = (
        *UserAdmin.list_filter,
        ('profile__section', admin.EmptyFieldListFilter),
        'profile__section',
        ('email', admin.EmptyFieldListFilter),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

    @admin.action(description="Change Profile Information")
    def bulk_change_profile(modeladmin, request, queryset):
        del request  # unused
        selected = queryset.values_list("pk", flat=True)
        ids_query = "&".join(f'id={pk}' for pk in selected)
        return HttpResponseRedirect(f"/admin/auth/user/bulk_change_profile/?{ids_query}")

    def change_profile(self, request: HttpRequest):
        if request.method == 'GET':
            user_ids = request.GET.getlist('id')
            return render(request, 'admin/change_profile.html', {
                'change_profile': {
                    'users': User.objects.filter(pk__in=user_ids),
                    'ids': user_ids,
                    'SECTION_CHOICES': SECTION_CHOICES,
                },
                **admin.site.each_context(request),
            })
        elif request.method != 'POST':
            return HttpResponse(status=405)

        raw_ids = request.POST.get('ids')
        if not raw_ids:
            return HttpResponse(status=400)
        ids = [int(raw_id) for raw_id in raw_ids.split(',')]

        profile = {
            key.replace('profile__', ''): value
            for key, value in request.POST.items()
            if key.startswith('profile__')
        }

        profiles = [
            Profile(user_id=user_id, **profile)
            for user_id in ids
        ]
        try:
            Profile.objects.bulk_create(
                profiles,
                update_conflicts=True,
                unique_fields=['user_id'],
                update_fields=list(profile.keys()),
            )
            messages.success(request, 'Updated profiles for {} users'.format(len(ids)))
        except Exception as e:
            messages.error(request, 'Failed to update profiles for {} users: {}'.format(len(ids), e))
            logging.exception(e)

        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))

    def get_urls(self):
        return [
            path(r'bulk_change_profile/', self.admin_site.admin_view(self.change_profile), name='change_profile')
        ] + super().get_urls()


admin.site.register(CommentAndSummary)
admin.site.register(Report, ReportAdmin)
admin.site.register(ProtectedClass)
admin.site.register(HateCrimesandTrafficking)
admin.site.register(ResponseTemplate, ResponseTemplateAdmin)
admin.site.register(DoNotEmail)
admin.site.register(JudicialDistrict, JudicialDistrictAdmin)
admin.site.register(RoutingSection, RoutingSectionAdmin)
admin.site.register(VotingMode, VotingModeAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(ReferralContact, ReferralContactAdmin)
admin.site.register(BannerMessage, BannerMessageAdmin)
admin.site.register(RoutingStepOneContact, RoutingStepOneContactAdmin)
admin.site.register(SavedSearch, SavedSearchAdmin)
admin.site.register(RetentionSchedule, RetentionScheduleAdmin)

# Activity stream already registers an Admin for Action, we want to replace it
admin.site.unregister(Action)
admin.site.unregister(Follow)
admin.site.register(Action, ActionAdmin)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
