from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class CrtAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        print("CrtAuthenticationBackend: CreateUser: Claims = ", claims)
        user = super(CrtAuthenticationBackend, self).create_user(claims)

        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.save()

        return user

    def update_user(self, user, claims):
        print("CrtAuthenticationBackend: UpdateUser: Claims = ", claims)
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.save()

        return user
