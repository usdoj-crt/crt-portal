from django.contrib import admin

from utils.admin import CrtModelAdmin
from .models import NewsWidgetColumnData


class NewsWidgetColumnAdmin(CrtModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ('name',)


admin.site.register(NewsWidgetColumnData, NewsWidgetColumnAdmin)
