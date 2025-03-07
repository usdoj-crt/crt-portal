from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render


def retrieve_and_save_next_url_in_session(request):
    print("CrtViews: Saving Next Url...")

    next_url = request.GET.get('next', '/')
    print("Next Url = ", next_url)

    request.session['next_page'] = next_url

    print("Request Session = ", request.session.__dict__)
    print("CrtViews: Next Url Saved.")

    request.session.modified = True
    request.session.save()


@login_required
def crt_loggedin_view(request):
    print("CrtLoggedinView: LoggedIn")
    print("Request Session = ", request.session.__dict__)
    print("Request User = ", request.user)

    print("next_url = ", request.session.get("next_page"))

    return render(request, 'loggedin.html')


class CrtLoginView(LoginView):
    authentication_form = AuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        print("CrtLoginView: Get")
        self.save_next_url(request)
        return super(CrtLoginView, self).get(request, *args, **kwargs)

    def save_next_url(self, request):
        retrieve_and_save_next_url_in_session(request)


class CrtAdminLoginView(LoginView):
    template_name = 'admin/login.html'

    def get(self, request, *args, **kwargs):
        print("CrtAdminLoginView: Get")
        self.save_next_url(request)
        return super(CrtAdminLoginView, self).get(request, *args, **kwargs)

    def save_next_url(self, request):
        retrieve_and_save_next_url_in_session(request)

