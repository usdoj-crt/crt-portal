from django.urls import re_path

from .views import redirect_to_shortened

app_name = 'shortener'


urlpatterns = [
    re_path(r'^.*/$', redirect_to_shortened)
]
