from django.shortcuts import render

from utils.static_data import read_static_json


def load_quotes(data_src):
    """Load the rotating banner quotes from a static JSON file.

    Returns a list of ``{"text": ..., "cite": ...}`` dicts. Missing or
    malformed data yields an empty list so the page still renders.
    """
    try:
        data = read_static_json(data_src)
    except (OSError, ValueError):
        return []
    return data.get('quotes', []) if isinstance(data, dict) else []


def election_integrity_view(request):
    quotes = load_quotes(
        data_src='data/election-integrity/quotes.json',
    )

    return render(request, 'election_integrity.html', {
        'quotes': quotes,
    })


def election_monitoring_view(request):
    # The map is split into one MapWidgetData record per administration (plus an
    # "all years" record). The page renders one map_widget include per entry and
    # a button controller swaps which one is visible. `key` is both the button's
    # value and the suffix of the record name: election-monitoring-map-<key>.
    administrations = [
        {'key': 'all', 'label': 'All years', 'default': False},
        {'key': '2025', 'label': 'Trump \u201925\u2013present', 'default': True},
        {'key': '2021', 'label': 'Biden \u201921\u2013\u201925', 'default': False},
        {'key': '2017', 'label': 'Trump \u201917\u2013\u201921', 'default': False},
        {'key': '2009', 'label': 'Obama \u201909\u2013\u201917', 'default': False},
        {'key': '2001', 'label': 'Bush \u201901\u2013\u201909', 'default': False},
    ]

    # Ensure exactly one administration is marked default, so only one map
    # shows on load. First flagged wins, falling back to the first entry.
    default_admin = next((a for a in administrations if a.get('default')), administrations[0])
    for admin in administrations:
        admin['default'] = admin is default_admin

    return render(request, 'election_monitoring.html', {
        'administrations': administrations,
    })
