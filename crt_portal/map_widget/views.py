from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from utils.static_data import resolve_reference_string
from .models import MapWidgetData


def _resolve_bullets(map_widget_data):
    """Resolve each action's bullet.image reference into a real URL, in place."""
    if not isinstance(map_widget_data, dict):
        return map_widget_data
    data = map_widget_data.get('data', map_widget_data)
    for feature in data.values():
        if not isinstance(feature, dict):
            continue
        for action in feature.get('actions', []) or []:
            bullet = action.get('bullet')
            if isinstance(bullet, dict) and bullet.get('image'):
                bullet['image'] = resolve_reference_string(bullet['image'])
    return map_widget_data


def map_widget_data_view(request, name):
    map_widget = get_object_or_404(MapWidgetData, name=name)
    resolved_data = _resolve_bullets(map_widget.data)
    return JsonResponse(resolved_data, safe=False)
