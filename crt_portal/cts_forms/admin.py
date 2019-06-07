from django.contrib import admin

from .models import State, ViolationReport, Choice

admin.site.register(State)
admin.site.register(ViolationReport)
admin.site.register(Choice)
