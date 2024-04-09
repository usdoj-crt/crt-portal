from django.urls import path

from .views import redirect_to_shortened

app_name = 'shortener'


urlpatterns = [
    path(r'<path:path>', redirect_to_shortened, name='shortener-redirect')
]
