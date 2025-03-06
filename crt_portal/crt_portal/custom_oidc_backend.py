from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        print("CrtAuthenticationBackend: VerifyClaims: Claims = ", claims)
        verified = super(CrtAuthenticationBackend, self).verify_claims(claims)

        return verified

    def create_user(self, claims):
        print("CrtAuthenticationBackend: CreateUser: Claims = ", claims)

        print("CrtAuthenticationBackend: Checking if user already exists before we create a new one...")
        user_exists = User.objects.filter(username=claims.get('sam_account_name'))
        if not user_exists:
            print("CrtAuthenticationBackend: User does not exist, creating a new one.")
            user = super(CrtAuthenticationBackend, self).create_user(claims)
            return user

        print("CrtAuthenticationBackend: User already exists... updating existing user.")
        user = User.objects.get(username=claims.get('sam_account_name'))
        user.email = claims.get('email')
        user.save()

        return user

    def update_user(self, user, claims):
        print("CrtAuthenticationBackend: UpdateUser: Claims = ", claims)
        user.save()

        return user
