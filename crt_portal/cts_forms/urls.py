from django.urls import path

from .views import IndexView, ShowView

app_name = 'crt_forms'

urlpatterns = [
    path('view/', IndexView, name='crt-forms-index'),
    path('<int:id>/', ShowView, name='crt-forms-show')
]
