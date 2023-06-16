from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import RefreshNotebookView

app_name = 'analytics'

urlpatterns = [
    path('refresh-notebook/<int:pk>', RefreshNotebookView.as_view(), name='notebook-refresh'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
