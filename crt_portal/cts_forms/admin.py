from django.contrib import admin

from .models import InternalHistory, Report

admin.site.register(InternalHistory)
admin.site.register(Report)
