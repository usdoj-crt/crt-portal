import os
import json
import urllib.parse
import posixpath

from django.conf import settings
from django.templatetags.static import static as static_url

from django.contrib.auth import logout as django_logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri
from django.shortcuts import redirect, render

from .decorators import portal_access_required


def _static_url_from_relative(base_static_path, relative_path):
    """Resolve a path that is relative to a static data file into a static URL.

    Agency-badge maps store image paths relative to the JSON file's own
    location (e.g. "../../../img/foo.svg"). Resolve that against the data file's
    directory, but clamp the result to the static root so paths that climb out
    of the static tree land back at the static root (e.g. "img/foo.svg") rather
    than escaping it.
    """
    base_parts = posixpath.dirname(base_static_path).split('/') if posixpath.dirname(base_static_path) else []
    for segment in relative_path.split('/'):
        if segment in ('', '.'):
            continue
        if segment == '..':
            if base_parts:
                base_parts.pop()
            # Once at the static root, further ".." segments are ignored so we
            # never resolve outside of it.
            continue
        base_parts.append(segment)
    normalized = '/'.join(base_parts)
    return static_url(normalized)


def _read_static_json(relative_path):
    """Read and parse a JSON file from the static source directory."""
    file_path = os.path.join(settings.BASE_DIR, 'static', *relative_path.split('/'))
    with open(file_path, encoding='utf-8') as json_file:
        return json.load(json_file)


def load_news_items(data_src, badge_mapping_src=None):
    """Load news card items from a static JSON file.

    For items without a `thumbnail`, resolve a `badge_image` from the agency
    badge map (when provided) so the template can render the agency seal as a
    fallback. Returns a list of item dicts ready for `partials/news_card.html`.
    """
    data = _read_static_json(data_src)
    items = data.get('items', []) if isinstance(data, dict) else []

    badge_mapping = {}
    if badge_mapping_src:
        try:
            raw_mapping = _read_static_json(badge_mapping_src)
            badge_mapping = {
                agency: _static_url_from_relative(badge_mapping_src, image_path)
                for agency, image_path in raw_mapping.items()
                if image_path
            }
        except (OSError, ValueError):
            badge_mapping = {}

    for item in items:
        thumbnail = item.get('thumbnail')
        if thumbnail:
            # Thumbnails are stored relative to the data file (like badge
            # images), so resolve them into a real static URL.
            item['thumbnail'] = _static_url_from_relative(data_src, thumbnail)
        elif item.get('agency'):
            item['badge_image'] = badge_mapping.get(item['agency'])

    return items


def election_integrity_view(request):
    news_items = load_news_items(
        data_src='data/news-card/test-data.json',
        badge_mapping_src='data/agency-badges/agency-badge-map.json',
    )
    return render(request, 'election_integrity.html', {'news_items': news_items})


def retrieve_and_save_next_url_in_session(request):
    next_url = request.GET.get('next', '/')
    request.session['next_page'] = next_url
    request.session.modified = True
    request.session.save()


def handle_oidc_login(request):
    return redirect('oidc_authentication_init')


def handle_oidc_logout(request):
    params = {
        'id_token_hint': request.session.get('oidc_id_token'),
        'post_logout_redirect_uri': settings.LOGOUT_REDIRECT_URL
    }

    django_logout(request)

    return redirect(f'{settings.OIDC_OP_LOGOUT_ENDPOINT}?{urllib.parse.urlencode(params)}')


@login_required
@portal_access_required
def crt_loggedin_view(request):
    next_page = request.session.get("next_page")
    if next_page:
        request.session.pop("next_page")
        if url_has_allowed_host_and_scheme(next_page, None):
            safe_url = iri_to_uri(next_page)
            return redirect(safe_url)
    return redirect('crt_landing_page')


def crt_logout_view(request):
    environment = os.environ.get('ENV', 'UNDEFINED')
    if environment in ['PRODUCTION', 'STAGE']:
        return handle_oidc_logout(request)
    return redirect('logout')


def crt_loggedout_view(request):
    return render(request, 'registration/logged_out.html')


class CrtLoginView(LoginView):
    authentication_form = AuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        self.save_next_url(request)
        environment = os.environ.get('ENV', 'UNDEFINED')
        if environment in ['PRODUCTION', 'STAGE']:
            return handle_oidc_login(request)
        return super(CrtLoginView, self).get(request, *args, **kwargs)

    def save_next_url(self, request):
        retrieve_and_save_next_url_in_session(request)


class CrtAdminLoginView(LoginView):
    template_name = 'admin/login.html'

    def get(self, request, *args, **kwargs):
        self.save_next_url(request)
        environment = os.environ.get('ENV', 'UNDEFINED')
        if environment in ['PRODUCTION', 'STAGE']:
            return handle_oidc_login(request)
        return super(CrtAdminLoginView, self).get(request, *args, **kwargs)

    def save_next_url(self, request):
        retrieve_and_save_next_url_in_session(request)
