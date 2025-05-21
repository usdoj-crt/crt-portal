import os
import urllib.parse

from django.conf import settings

from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri
from django.shortcuts import redirect, render
from django.middleware.csrf import get_token

from .decorators import portal_access_required


def retrieve_and_save_next_url_in_session(request):
    next_url = request.GET.get('next', '/')
    request.session['next_page'] = next_url
    request.session.modified = True
    request.session.save()


def handle_oidc_logout(id_token):
    base_uri = f'{settings.login_base_url}'
    logout_uri = f'{settings.LOGOUT_REDIRECT_URL}'
    logout_redirect_uri = base_uri + logout_uri

    url = f'{settings.OIDC_OP_LOGOUT_ENDPOINT}?'
    params = {
        'id_token_hint': id_token,
        'post_logout_redirect_uri': logout_redirect_uri
    }
    request = url + urllib.parse.urlencode(params)
    print("Handling oidc logout: Request URL =", request)
    return redirect(request)


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
        id_token = request.session.get('oidc_id_token')
        csrf_token = get_token(request)
        print("CrtLogout Debug: Id Token =", id_token)
        print("CrtLogout Debug: csrf_token =", csrf_token)
        handle_oidc_logout(id_token)
    return redirect('logout')


def crt_loggedout_view(request):
    return render(request, 'registration/logged_out.html')


class CrtLoginView(LoginView):
    authentication_form = AuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        self.save_next_url(request)
        return super(CrtLoginView, self).get(request, *args, **kwargs)

    def save_next_url(self, request):
        retrieve_and_save_next_url_in_session(request)


class CrtAdminLoginView(LoginView):
    template_name = 'admin/login.html'

    def get(self, request, *args, **kwargs):
        self.save_next_url(request)
        return super(CrtAdminLoginView, self).get(request, *args, **kwargs)

    def save_next_url(self, request):
        retrieve_and_save_next_url_in_session(request)
