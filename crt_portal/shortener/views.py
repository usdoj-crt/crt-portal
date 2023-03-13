from django.shortcuts import redirect
from django.urls.exceptions import Http404
from .models import ShortenedURL


def redirect_to_shortened(request):
    try:
        without_link = request.path.split('/')[-2:]
        shortname = '/'.join(without_link).strip('/')

        return redirect(ShortenedURL.objects.get(pk=shortname))
    except ShortenedURL.DoesNotExist:
        raise Http404()
