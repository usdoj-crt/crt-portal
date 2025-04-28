from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls.exceptions import Http404
from django.http import JsonResponse
from .models import ShortenedURL
from crt_portal.decorators import active_user_required


def redirect_to_shortened(request, *, path):
    shortname = path.strip('/')
    try:
        return redirect(ShortenedURL.objects.get(pk=shortname))
    except ShortenedURL.DoesNotExist:
        raise Http404()


@login_required
@active_user_required
def preview_urlify(request, *, prefix=''):
    name = request.GET.get('name')
    return JsonResponse({
        'url': ShortenedURL.urlify(name, prefix=prefix),
    })
