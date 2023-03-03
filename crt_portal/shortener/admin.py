from django.contrib import admin
from .models import ShortenedURL


class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('pk', 'destination')


admin.site.register(ShortenedURL, ShortenedURLAdmin)
