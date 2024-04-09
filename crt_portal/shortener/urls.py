from django.urls import path

from .views import redirect_to_shortened, preview_urlify

app_name = 'shortener'


urlpatterns = [
    path(r'urlify/<path:prefix>', preview_urlify, name='urlify-preview-prefix'),
    path(r'urlify/', preview_urlify, name='urlify-preview'),
    path(r'<path:path>', redirect_to_shortened, name='shortener-redirect')
]
