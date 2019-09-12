from django.urls import path

from .views import IndexView

app_name = 'crt_forms'

urlpatterns = [
    path('view', IndexView, name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
]
