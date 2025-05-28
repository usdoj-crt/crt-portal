from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_username(email, claims):
    return email


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def _store_issuer_in_session(self, claims):
        session = self.request.session

        print("CrtAuthenticationBackend Debug: Claims = ", claims)

        issuer = claims.get("iss", None)
        print("CrtAuthenticationBackend Debug: Issuer = ", issuer)

        session['oidc_issuer'] = issuer
        session.modified = True
        session.save()

        print("CrtAuthenticationBackend Debug: session oidc_issuer = ", session.get("oidc_issuer", ""))

    def create_user(self, claims):
        self._store_issuer_in_session(claims)

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

    def update_user(self, user, claims):
        self._store_issuer_in_session(claims)

        user = super(CrtAuthenticationBackend, self).update_user(user, claims)
        return user
