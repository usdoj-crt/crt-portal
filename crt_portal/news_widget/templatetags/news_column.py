from django import template

from news_widget.models import NewsWidgetColumnData

register = template.Library()


@register.inclusion_tag('partials/news_column.html')
def render_news_column(name, labelledby=''):
    try:
        column = NewsWidgetColumnData.objects.get(name=name)
        items = column.data or []
    except NewsWidgetColumnData.DoesNotExist:
        items = []

    return {
        'items': items,
        'labelledby': labelledby,
    }
