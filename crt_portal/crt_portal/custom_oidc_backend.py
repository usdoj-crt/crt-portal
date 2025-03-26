from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = None
        account_name = claims.get('adsamAccountName')
        user_exists = User.objects.filter(username=account_name).exists()

        if user_exists:
            print(f"CustomOidcBackend: INFO: User with {account_name} found.")
            user = User.objects.get(username=account_name)
        else:
            print(f"CustomOidcBackend: INFO: User with {account_name} does not exist. Creating a new user with email instead.")
            user = super(CrtAuthenticationBackend, self).create_user(claims)

        user.email = claims.get('email')
        user.save()

        print(f"CustomOidcBackend: INFO: Updated user info: {user}")
        return user
