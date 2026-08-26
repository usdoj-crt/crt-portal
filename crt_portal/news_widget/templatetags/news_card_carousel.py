from utils.static_data import resolve_reference_string

from django import template

from news_widget.models import NewsWidgetCardsData


register = template.Library()


@register.inclusion_tag('news_widget/news_carousel.html')
def render_news_card_carousel(name, label='', overlay_buttons='', classes=''):
    try:
        card_set = NewsWidgetCardsData.objects.get(name=name)
        raw_cards = card_set.data or []
    except NewsWidgetCardsData.DoesNotExist:
        raw_cards = []

    items = []
    for card in raw_cards:
        if not isinstance(card, dict):
            continue
        item = {
            'type': card.get('type', ''),
            'date': card.get('date', ''),
            'linkUrl': card.get('linkUrl', ''),
            'linkText': card.get('linkText', ''),
            'source': card.get('source', ''),
            'thumbnail': resolve_reference_string(card.get('thumbnail')),
            'placeholder_thumbnail': resolve_reference_string(card.get('placeholder_thumbnail')),
        }

        items.append(item)

    return {
        'items': items,
        'label': label,
        'overlay_buttons': overlay_buttons,
        'classes': classes,
    }
