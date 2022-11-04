import logging
from cts_forms.admin import ReadOnlyModelAdmin, csv, Echo, iter_queryset, format_export_message
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import StreamingHttpResponse

from .models import TMSEmail

TMS_FIELDS = ['id', 'tms_id', 'subject', 'body', 'recipient', 'status', 'error_message', 'report_id', 'created_at', 'completed_at', 'purpose']

logger = logging.getLogger(__name__)


def _serialize_tms(data):
    """Preserve headers while rendering TMS_FIELDS for inbound actions"""
    if isinstance(data, TMSEmail):
        return [getattr(data, field) for field in TMS_FIELDS]
    return data


def export_tms_as_csv(modeladmin, request, queryset):
    """
    Stream actions as csv
    Log all use
    """
    writer = csv.writer(Echo(), quoting=csv.QUOTE_ALL)
    iterator = iter_queryset(queryset, TMS_FIELDS)
    response = StreamingHttpResponse((writer.writerow(_serialize_tms(tms)) for tms in iterator),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="tms_export.csv"'

    logger.info(format_export_message(request, queryset.count(), 'tms log entries'))
    return response
export_tms_as_csv.allowed_permissions = ('view',)  # noqa


class TMSEmailAdmin(ReadOnlyModelAdmin):
    search_fields = ['recipient', 'report__public_id', 'error_message']
    list_display = ('tms_id', 'tms_detail_url', 'recipient', 'report', 'status', 'created_at', 'completed_at', 'purpose')
    date_hierarchy = 'created_at'
    list_filter = ('status', 'created_at', 'purpose')
    ordering = ['-created_at']

    def tms_detail_url(self, obj):
        return format_html('<a href="%s">View & update</a>' % (reverse('tms:tms-admin-message', kwargs={"tms_id": obj.tms_id})))

    tms_detail_url.short_description = 'TMS details'
    actions = [export_tms_as_csv]


admin.site.register(TMSEmail, TMSEmailAdmin)
