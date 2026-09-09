from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from utils.static_data import resolve_reference_string
from .models import MapWidgetData


def _resolve_blocks(blocks):
    """Resolve image references within a list of display blocks, in place.

    Walks the block vocabulary the USA map widget renders: `list` blocks carry
    `items[].bullet.image` references, and `row` blocks nest one level of child
    blocks. Any `static:` (or http) reference is resolved to a real URL so the
    browser can load it.
    """
    for block in blocks or []:
        if not isinstance(block, dict):
            continue
        block_type = block.get('type')
        if block_type == 'list':
            for item in block.get('items', []) or []:
                bullet = item.get('bullet') if isinstance(item, dict) else None
                if isinstance(bullet, dict) and bullet.get('image'):
                    bullet['image'] = resolve_reference_string(bullet['image'])


def _resolve_record(record):
    """Resolve bullet references across every display surface of one record."""
    if not isinstance(record, dict):
        return
    display = record.get('display')
    if not isinstance(display, dict):
        return
    for surface in display.values():
        _resolve_blocks(surface)


def _resolve_bullets(map_widget_data):
    """Resolve every bullet.image reference into a real URL, in place.

    Covers each feature record under `features` as well as the `default` record.
    """
    if not isinstance(map_widget_data, dict):
        return map_widget_data
    features = map_widget_data.get('features', {})
    if isinstance(features, dict):
        for record in features.values():
            _resolve_record(record)
    _resolve_record(map_widget_data.get('default'))
    return map_widget_data


def map_widget_data_view(request, name):
    map_widget = get_object_or_404(MapWidgetData, name=name)
    resolved_data = _resolve_bullets(map_widget.data)
    return JsonResponse(resolved_data, safe=False)
