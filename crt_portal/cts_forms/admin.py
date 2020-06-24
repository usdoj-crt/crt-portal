import csv

from django.contrib import admin
from django.http import StreamingHttpResponse

from .models import (CommentAndSummary, HateCrimesandTrafficking,
                     ProtectedClass, Report, ResponseTemplate)


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def export_as_csv(modeladmin, request, queryset):
    """Stream all fields of selected reports as CSV"""
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    headers = [field.name for field in Report._meta.fields]
    rows = [headers]
    for report in queryset:
        rows.append([getattr(report, field) for field in headers])
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response
export_as_csv.allowed_permissions = ('view',)  # noqa


class ReportAdmin(admin.ModelAdmin):
    """
    View-only report admin providing filtering and export functionality
    """
    list_display = ['public_id', 'status', 'assigned_section', 'create_date', 'modified_date', 'assigned_to']
    list_filter = ['status', 'create_date', 'modified_date', 'assigned_section', 'servicemember',
                   'hate_crime', 'primary_complaint', 'assigned_to']
    ordering = ['public_id']
    actions = [export_as_csv]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.register(CommentAndSummary)
admin.site.register(Report, ReportAdmin)
admin.site.register(ProtectedClass)
admin.site.register(HateCrimesandTrafficking)
admin.site.register(ResponseTemplate)
