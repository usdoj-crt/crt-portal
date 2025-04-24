from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def update_user(self, user, claims):
        if not user.is_active:
            return redirect('form/landing/')

    def create_user(self, claims):
        user = None
        account_name = claims.get('adsamAccountName')
        user_exists = User.objects.filter(username=account_name).exists()

        if user_exists:
            user = User.objects.get(username=account_name)
        else:
            user = super(CrtAuthenticationBackend, self).create_user(claims)

        user.email = claims.get('email')
        user.is_active = False
        user.save()

        return redirect('form/landing/')
