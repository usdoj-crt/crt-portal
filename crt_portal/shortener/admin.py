from django.contrib import admin
from django.utils.html import mark_safe

from .models import ShortenedURL
from utils.admin import CrtModelAdmin


class ShortenedURLAdmin(CrtModelAdmin):
    list_display = ('pk', 'destination', 'current_shortname')
    readonly_fields = ('current_shortname',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'shortname' in form.changed_data:
            ShortenedURL.objects.get(pk=request.POST['current_shortname']).delete()

    @admin.display(description='Current Link')
    def current_shortname(self, obj):
        original = f'<input type="hidden" name="current_shortname" value="{obj.pk}"/>'
        if not obj.pk or not obj.enabled:
            return mark_safe('This must be enabled and saved for the link to work.')
        short_url = obj.get_short_url()
        link = f'<a href="{short_url}">{short_url}</a>'
        return mark_safe(original + link)


admin.site.register(ShortenedURL, ShortenedURLAdmin)
