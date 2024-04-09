from django.shortcuts import redirect
from django.urls.exceptions import Http404
from .models import ShortenedURL


def redirect_to_shortened(request, *, path):
    shortname = path.strip('/')
    try:
        return redirect(ShortenedURL.objects.get(pk=shortname))
    except ShortenedURL.DoesNotExist:
        raise Http404()
