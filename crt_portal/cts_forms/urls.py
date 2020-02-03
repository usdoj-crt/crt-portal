from django.urls import path

from .views import IndexView, ShowView

app_name = 'crt_forms'


urlpatterns = [
    path('view/<int:id>/', ShowView.as_view(), name='crt-forms-show'),
    path('view/', IndexView, name='crt-forms-index'),
]
