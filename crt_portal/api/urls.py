from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import ResponseList, ResponseDetail, ReportCountView, ReportList, ReportDetail, RelatedReports, FormLettersIndex, api_root

app_name = 'api'

urlpatterns = [
    path('', api_root, name='api-base'),
    path('reports/', ReportList.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetail.as_view(), name='report-detail'),
    path('responses/', ResponseList.as_view(), name='response-list'),
    path('responses/<int:pk>/', ResponseDetail.as_view(), name='response-detail'),
    path('report-count/', ReportCountView.as_view(), name='report-count'),
    path('report-count/<int:pk>', ReportCountView.as_view(), name='report-count'),
    path('related-reports/', RelatedReports.as_view(), name='related-reports'),
    path('form-letters/', FormLettersIndex.as_view(), name='form-letters'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
