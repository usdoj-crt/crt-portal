from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.utils.http import is_safe_url
from django.shortcuts import redirect


def retrieve_and_save_next_url_in_session(request):
    next_url = request.GET.get('next', '/')
    request.session['next_page'] = next_url
    request.session.modified = True
    request.session.save()


@login_required
def crt_loggedin_view(request):
    next_url = request.session.get("next_page")
    if next_url and is_safe_url(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
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
