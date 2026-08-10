from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import MapWidgetData


def map_widget_data_view(request, name):
    widget_data = get_object_or_404(MapWidgetData, name=name)
    return JsonResponse(widget_data.data, safe=False)
