from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import iri_to_uri
from django.shortcuts import redirect
from django.urls import reverse


def retrieve_and_save_next_url_in_session(request):
    next_url = request.GET.get('next', '/')
    request.session['next_page'] = next_url
    request.session.modified = True
    request.session.save()


@login_required
def crt_loggedin_view(request):
    print("CrtLogin: Logged In")
    next_page = request.session.get("next_page")
    if next_page:
        print("CrtLogin: Next Page = ", next_page)
        next_url = reverse('crt_landing_page') + next_page
        print("CrtLogin: Next Url = ", next_url)
        if url_has_allowed_host_and_scheme(next_url, None):
            safe_url = iri_to_uri(next_url)
            print("CrtLogin: Safe Url = ", safe_url)
            return redirect(safe_url)
    return redirect('crt_landing_page')


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
