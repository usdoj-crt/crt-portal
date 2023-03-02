"""Contains models for deeply customizing OAuth2 behavior.

For more info, see:
  https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html#settings
"""
from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    """Defines what information is shown to Jupyter about logged in users."""
    oidc_claim_scope = None

    def get_additional_claims(self, request):
        if not request.user.is_superuser:
            # Don't allow non-superusers to log in.
            return {}
        return {
            "username": request.user.username,
            "email": request.user.email,
        }
