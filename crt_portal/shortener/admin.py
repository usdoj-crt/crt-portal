from django.contrib import admin
from django.utils.html import mark_safe

from .models import ShortenedURL


class ShortenedURLAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'vendor/qrcode.js',
            'js/admin_copy.js',
            'js/absolute_url.js',
            'js/qr.js',
        )
        css = {
            'all': ('css/compiled/admin.css',)
        }

    list_display = ('pk', 'destination', 'current_shortname', 'full_url')
    readonly_fields = ('current_shortname', 'full_url', 'qrcode')

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

    @admin.display(description='Full URL')
    def full_url(self, obj):
        short_url = obj.get_short_url()
        return mark_safe(f'<input aria-label="Full URL" disabled="disabled" class="admin-copy absolute-url full-url" value="{short_url}"/>')

    @admin.display(description='QR (Camera-readable version of the Current Link)')
    def qrcode(self, obj):
        del obj
        return mark_safe('<div class="qrcode" data-qr-source=".full-url"></div>')


admin.site.register(ShortenedURL, ShortenedURLAdmin)
