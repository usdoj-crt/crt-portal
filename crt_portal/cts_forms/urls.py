from django.urls import path

from .views import IndexView

app_name = 'crt_forms'

urlpatterns = [
    path('view', IndexView, name='crt-forms-index'),
]
