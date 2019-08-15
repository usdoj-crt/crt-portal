from django.contrib import admin

from .models import InternalHistory, Report, ProtectedClass

admin.site.register(InternalHistory)
admin.site.register(Report)
admin.site.register(ProtectedClass)
