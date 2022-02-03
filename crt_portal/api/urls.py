from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import ReportList, ReportDetail, api_root

app_name = 'api'

urlpatterns = [
    path('', api_root, name='api-base'),
    path('reports/', ReportList.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetail.as_view(), name='report-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
