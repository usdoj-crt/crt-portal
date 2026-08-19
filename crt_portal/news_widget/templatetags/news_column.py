from datetime import datetime

from django import template

from news_widget.models import NewsWidgetColumnData


register = template.Library()


def _format_display_date(value):
    """Format a stored ISO date ('YYYY-MM-DD') for display, e.g. 'Feb 26, 2026'.

    Values that are not ISO dates (such as already-formatted legacy strings)
    are returned unchanged, so older records still display correctly.
    """
    if not isinstance(value, str):
        return value
    try:
        parsed = datetime.strptime(value.strip(), '%Y-%m-%d')
    except ValueError:
        return value
    return parsed.strftime('%b %d, %Y')


@register.inclusion_tag('partials/news_column.html')
def render_news_column(name, labelledby=''):
    try:
        column = NewsWidgetColumnData.objects.get(name=name)
        raw_items = column.data or []
    except NewsWidgetColumnData.DoesNotExist:
        raw_items = []

    items = [
        {
            'date': _format_display_date(item.get('date', '')),
            'title': item.get('title', ''),
            'link': item.get('link', ''),
        }
        for item in raw_items
        if isinstance(item, dict)
    ]

    return {
        'items': items,
        'labelledby': labelledby,
    }
