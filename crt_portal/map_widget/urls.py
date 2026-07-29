from django.urls import path

from .views import map_widget_data_view

app_name = 'map_widget'

urlpatterns = [
    path('data/<str:name>.json', map_widget_data_view, name='data'),
]
