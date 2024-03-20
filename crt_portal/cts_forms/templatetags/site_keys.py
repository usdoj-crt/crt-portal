from django.conf import settings


def recaptcha_site_key(request):
    """Adds the recaptcha site key to the request context."""
    client_defeat = request.headers.get('X-Captcha-Defeat')
    server_defeat = settings.RECAPTCHA['DEFEAT_KEY']
    if server_defeat and client_defeat == server_defeat:
        return {'RECAPTCHA': {'site_key': ''}}

    try:
        return {'RECAPTCHA': {'site_key': settings.RECAPTCHA['SITE_KEY']}}
    except KeyError:
        return {'RECAPTCHA': {'site_key': ''}}
