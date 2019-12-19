from django.contrib import admin

from .models import InternalHistory, Report, ProtectedClass, HateCrimesandTrafficking

admin.site.register(InternalHistory)
admin.site.register(Report)
admin.site.register(ProtectedClass)
admin.site.register(HateCrimesandTrafficking)
