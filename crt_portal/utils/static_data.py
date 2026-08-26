import json
import os

from django.conf import settings
from django.templatetags.static import static


def read_static_json(relative_path):
    """Read and parse a JSON file from the static source directory."""
    file_path = os.path.join(settings.BASE_DIR, 'static', *relative_path.split('/'))
    with open(file_path, encoding='utf-8') as json_file:
        return json.load(json_file)


def resolve_reference_string(value):
    """Resolve a prefixed reference string into a URL, or None.

    Contract:
      - empty/None            -> None
      - "static:<key>"        -> static(<key>)
      - "http://" / "https://"-> used verbatim (external resource)
      - "db:<name>"           -> None for now (future DB-backed spike)
      - anything else         -> None (fail safe)
    """
    if not value or not isinstance(value, str):
        return None

    value = value.strip()

    if value.startswith('static:'):
        return static(value.removeprefix('static:'))

    if value.startswith('http://') or value.startswith('https://'):
        return value

    # TODO: If we ever add DB-backed references (e.g. thumbnails stored as
    # binary blobs), resolve them here. None for now.
    if value.startswith('db:'):
        return None

    return None
