from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):

    def create_user(self, claims):
        user = super(CrtAuthenticationBackend, self).create_user(claims)

        user.email = claims.get('email')

        try:
            first_name = claims['given_name']
            if first_name:
                user.first_name = first_name

            last_name = claims['family_name']
            if last_name:
                user.last_name = last_name
        except Exception:
            print("CustomOidcBackend CreateUser: ERROR when getting first and last names from claims. Claims = ", claims)

        user.is_active = True
        user.save()

        return user
