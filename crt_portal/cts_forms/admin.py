from django.contrib import admin

from .models import (Comment, HateCrimesandTrafficking, InternalHistory,
                     ProtectedClass, Report)

admin.site.register(InternalHistory)
admin.site.register(Report)
admin.site.register(ProtectedClass)
admin.site.register(HateCrimesandTrafficking)
admin.site.register(Comment)

