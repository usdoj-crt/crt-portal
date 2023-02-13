from django.urls import path

from .views import config_view, index_view, render_email

app_name = 'cms'

urlpatterns = [
    path('', index_view, name='cms-index'),
    path('config.yml', config_view, name='cms-config'),
    path('render', render_email, name='cms-render'),
]
