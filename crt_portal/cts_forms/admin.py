from django.contrib import admin

from .models import CommentAndSummary, Report, ProtectedClass, HateCrimesandTrafficking

admin.site.register(CommentAndSummary)
admin.site.register(Report)
admin.site.register(ProtectedClass)
admin.site.register(HateCrimesandTrafficking)
