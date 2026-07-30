from django.contrib import admin

from utils.admin import CrtModelAdmin
from .models import MapWidgetData


class MapWidgetDataAdmin(CrtModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ('name',)


admin.site.register(MapWidgetData, MapWidgetDataAdmin)
