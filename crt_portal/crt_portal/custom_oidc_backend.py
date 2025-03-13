from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        verified = super(CrtAuthenticationBackend, self).verify_claims(claims)
        user_exists = User.objects.filter(email=claims.get('email')).exists()

        if verified and user_exists:
            return True
        return False

    def create_user(self, claims):
        user_exists = User.objects.filter(username=claims.get('sam_account_name')).exists()
        if not user_exists:
            user = super(CrtAuthenticationBackend, self).create_user(claims)
            return user
        user = User.objects.get(username=claims.get('sam_account_name'))
        user.email = claims.get('email')
        user.save()

        return user
