import os
import urllib.parse

from django.conf import settings

from django.contrib.auth import logout as django_logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri
from django.shortcuts import redirect, render

from .decorators import portal_access_required


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
