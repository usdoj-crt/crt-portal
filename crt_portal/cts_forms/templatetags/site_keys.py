from django.conf import settings


def challenge_site_key(request):
    """Adds the challenge site key to the request context."""
    client_defeat = request.headers.get('X-Challenge-Defeat')
    server_defeat = settings.CHALLENGE['DEFEAT_KEY']
    if server_defeat and client_defeat == server_defeat:
        return {'CHALLENGE': {'site_key': ''}}

    try:
        return {'CHALLENGE': {'site_key': settings.CHALLENGE['SITE_KEY']}}
    except KeyError:
        return {'CHALLENGE': {'site_key': ''}}
