from utils.static_data import resolve_reference_string

from django import template

from news_widget.models import NewsWidgetCardsData


register = template.Library()


def _load_card_set_items(name):
    """Return the resolved list of card items for a card set by name.

    Fetches the ``NewsWidgetCardsData`` record (editable in the admin panel)
    and normalizes each card into the dict shape expected by
    ``news_widget/news_card.html``. Returns an empty list if the set is
    missing so callers can render gracefully.
    """
    try:
        card_set = NewsWidgetCardsData.objects.get(name=name)
        raw_cards = card_set.data or []
    except NewsWidgetCardsData.DoesNotExist:
        raw_cards = []

    items = []
    for card in raw_cards:
        if not isinstance(card, dict):
            continue
        items.append({
            'type': card.get('type', ''),
            'date': card.get('date', ''),
            'linkUrl': card.get('linkUrl', ''),
            'linkText': card.get('linkText', ''),
            'source': card.get('source', ''),
            'thumbnail': resolve_reference_string(card.get('thumbnail')),
            'placeholder_thumbnail': resolve_reference_string(card.get('placeholder_thumbnail')),
        })

    return items


@register.inclusion_tag('news_widget/news_carousel.html')
def render_news_card_carousel(name, label='', overlay_buttons='', clickable_thumbnail='', classes=''):
    return {
        'items': _load_card_set_items(name),
        'label': label,
        'overlay_buttons': overlay_buttons,
        'clickable_thumbnail': clickable_thumbnail,
        'classes': classes,
    }


@register.inclusion_tag('news_widget/news_card_set.html')
def render_news_card_set(name, show_thumbnail='', clickable_thumbnail=''):
    """Render a card set as a plain group of news cards (no carousel).

    Used for the "Featured stories" style layout, where cards are laid out
    directly rather than in a scrollable carousel.
    """
    return {
        'items': _load_card_set_items(name),
        'show_thumbnail': show_thumbnail,
        'clickable_thumbnail': clickable_thumbnail,
    }
