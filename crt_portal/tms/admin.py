from cts_forms.admin import ReadOnlyModelAdmin
from django.contrib import admin

from .models import TMSEmail


class TMSEmailAdmin(ReadOnlyModelAdmin):
    search_fields = ['recipient', 'report__public_id', 'error_message']
    list_display = ('tms_id', 'recipient', 'report', 'status', 'created_at', 'completed_at', 'purpose')
    date_hierarchy = 'created_at'
    list_filter = ('status', 'created_at', 'purpose')


admin.site.register(TMSEmail, TMSEmailAdmin)
