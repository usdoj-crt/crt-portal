from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from utils.static_data import resolve_reference_string
from .models import MapWidgetData


def _resolve_bullets(data):
    """Resolve each action's bullet.image reference into a real URL, in place."""
    if not isinstance(data, dict):
        return data
    for state in data.values():
        if not isinstance(state, dict):
            continue
        for action in state.get('actions', []) or []:
            bullet = action.get('bullet')
            if isinstance(bullet, dict) and bullet.get('image'):
                bullet['image'] = resolve_reference_string(bullet['image'])
    return data


def map_widget_data_view(request, name):
    widget_data = get_object_or_404(MapWidgetData, name=name)
    data = _resolve_bullets(widget_data.data)
    return JsonResponse(data, safe=False)
