"""Contains models for deeply customizing OAuth2 behavior.

For more info, see:
  https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html#settings
"""
import logging
from oauth2_provider.oauth2_validators import OAuth2Validator

JUPYTER_PERMISSION_LEVELS = [
    'jupyter_editor',
    'jupyter_superuser',
]


class CustomOAuth2Validator(OAuth2Validator):
    """Defines what information is shown to Jupyter about logged in users."""
    oidc_claim_scope = None

    def get_additional_claims(self, request):
        groups = [
            permission
            if request.user.has_perm(f'analytics.{permission}')
            else None
            for permission in JUPYTER_PERMISSION_LEVELS
        ]

        claims = {
            "username": request.user.username,
            "email": request.user.email,
            "groups": [group for group in groups if group],
        }

        logging.info(f"Authenticated Jupyterhub user: {claims}")

        return claims
