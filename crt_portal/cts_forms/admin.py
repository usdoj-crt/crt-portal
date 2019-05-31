from django.contrib import admin

from .models import ViolationReport, Choice

admin.site.register(ViolationReport)
admin.site.register(Choice)
