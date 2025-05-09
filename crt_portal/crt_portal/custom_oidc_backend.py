from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = None
        user_exists = False

        account_name = claims.get('adsamAccountName', None)
        if account_name:
            user_exists = User.objects.filter(username=account_name).exists()

        if user_exists:
            user = User.objects.get(username=account_name)
        else:
            user = super(CrtAuthenticationBackend, self).create_user(claims)

        user.email = claims.get('email')
        user.is_active = True
        user.save()

        return user
