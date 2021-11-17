from cts_forms.admin import ReadOnlyModelAdmin
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import TMSEmail


class TMSEmailAdmin(ReadOnlyModelAdmin):
    search_fields = ['recipient', 'report__public_id', 'error_message']
    list_display = ('tms_id', 'tms_detail_url', 'recipient', 'report', 'status', 'created_at', 'completed_at', 'purpose')
    date_hierarchy = 'created_at'
    list_filter = ('status', 'created_at', 'purpose')
    ordering = ['-created_at']

    def tms_detail_url(self, obj):
        return format_html('<a href="%s">View status</a>' % (reverse('tms:tms-admin-message', kwargs={"tms_id": obj.tms_id})))

    tms_detail_url.short_description = 'TMS details'


admin.site.register(TMSEmail, TMSEmailAdmin)
