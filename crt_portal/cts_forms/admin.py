from django.contrib import admin

from .models import State, ViolationReport

admin.site.register(State)
admin.site.register(ViolationReport)
