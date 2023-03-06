import csv
import logging

from actstream.models import Action, Follow
from django.apps import apps
from django.contrib import admin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import StreamingHttpResponse
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from django.urls import reverse
from django.db.models.functions import Lower

from .models import (CommentAndSummary, HateCrimesandTrafficking, Profile,
                     ProtectedClass, Report, ResponseTemplate, DoNotEmail,
                     JudicialDistrict, RoutingSection, RoutingStepOneContact,
                     VotingMode, Campaign)
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


def iter_queryset(queryset, headers):
    """
    The iterator provided by queryset.iterator isn't adequate here

    We add headers to our output

    We also need to traverse M2M relationships for at least 1 field
    and want tos use prefetch_related to avoid a query for each instance
    queryset.iterator ignores `prefetch_related` so instead we paginate
    through the queryset to reduce the number of total queries required
    """
    yield headers
    paginator = Paginator(queryset, 2000)
    for i in range(paginator.num_pages):
        yield from paginator.get_page(i + 1)


def _serialize_report_export(data):
    """
    Customize the rendering of protected_class and summary instances
    while rendering headers as-is
    """
    if isinstance(data, Report):
        row = [getattr(data, field) for field in REPORT_FIELDS]
        row.append('; '.join([str(pc) for pc in data.protected_class.all()]))
        if data.internal_summary:
            # incoming summaries are sorted by descending modified_date the first is the most recent
            row.append(data.internal_summary[0].note)
        else:
            row.append('')
        return row
    return data


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

    summaries = CommentAndSummary.objects.filter(is_summary=True).order_by('-modified_date')
    queryset = queryset.prefetch_related('protected_class',
                                         Prefetch('internal_comments', queryset=summaries, to_attr='internal_summary')
                                         ).order_by('id')
    iterator = iter_queryset(queryset, headers)

    response = StreamingHttpResponse((writer.writerow(_serialize_report_export(report)) for report in iterator),
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


class ReportAdmin(ReadOnlyModelAdmin):
    """
    View-only report admin providing filtering and export functionality
    """
    list_display = ['public_id', 'status', 'assigned_section', 'create_date', 'modified_date', 'assigned_to']
    list_filter = ['status', 'viewed', 'create_date', 'modified_date', 'assigned_section', 'servicemember',
                   'hate_crime', 'primary_complaint', 'assigned_to']
    ordering = ['public_id']
    actions = [export_reports_as_csv]


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


class CampaignAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin_copy.js',)
        css = {
            'all': ('css/compiled/admin.css',)
        }

    list_display = ['uuid', 'internal_name', 'shorten_url', 'campaign_url']
    readonly_fields = ['campaign_url', 'shorten_url']

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


class ResponseTemplateAdmin(admin.ModelAdmin):
    exclude = ['is_user_created']


admin.site.register(CommentAndSummary)
admin.site.register(Report, ReportAdmin)
admin.site.register(ProtectedClass)
admin.site.register(HateCrimesandTrafficking)
admin.site.register(ResponseTemplate, ResponseTemplateAdmin)
admin.site.register(Profile)
admin.site.register(DoNotEmail)
admin.site.register(JudicialDistrict, JudicialDistrictAdmin)
admin.site.register(RoutingSection, RoutingSectionAdmin)
admin.site.register(VotingMode, VotingModeAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(RoutingStepOneContact, RoutingStepOneContactAdmin)

# Activity stream already registers an Admin for Action, we want to replace it
admin.site.unregister(Action)
admin.site.unregister(Follow)
admin.site.register(Action, ActionAdmin)
