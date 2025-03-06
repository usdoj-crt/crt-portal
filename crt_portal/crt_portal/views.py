from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render


def crt_loggedin_view(request):
    print("CrtLoggedinView: LoggedIn")
    print("Request Session = ", request.session.__dict__)
    print("Request User = ", request.user)

    print("next_url = ", request.session.get("next_url"))

    return render(request, 'loggedin.html')


class CrtLoginView(LoginView):
    authentication_form = AuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        print("CrtLoginView: Get")
        self.save_next_url(request)
        return super(CrtLoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("CrtLoginView: Post")
        self.save_next_url(request)
        return super(CrtLoginView, self).post(request, *args, **kwargs)

    def save_next_url(self, request):
        print("CrtLoginView: Saving Next Url...")
        next_url = super(CrtLoginView, self).get_default_redirect_url()
        print("Next Url = ", next_url)
        request.session['next_page'] = next_url
        print("Request Session = ", request.session.__dict__)
        request.session.modified = True
        request.session.save()
        print("CrtLoginView: Next Url Saved.")
