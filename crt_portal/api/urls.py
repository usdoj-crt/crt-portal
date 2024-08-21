from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import ResponseList, ResponseDetail, ReportSummary, ReportCountView, ReportCWs, ReportList, ReportDetail, RelatedReports, FormLettersIndex, api_root, ResponseTemplateFilePreview, ResponseTemplateFormPreview, ResponseAction, ProformAttachmentView, ReportEdit

app_name = 'api'

urlpatterns = [
    path('', api_root, name='api-base'),
    path('report-edit/', ReportEdit.as_view(), name='report-edit'),
    path('reports/', ReportList.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetail.as_view(), name='report-detail'),
    path('responses/', ResponseList.as_view(), name='response-list'),
    path('responses/<int:pk>/', ResponseDetail.as_view(), name='response-detail'),
    path('preview-response/<filename>', ResponseTemplateFilePreview.as_view(), name='preview-response-file'),
    path('preview-response/', ResponseTemplateFormPreview.as_view(), name='preview-response-form'),
    path('report-count/', ReportCountView.as_view(), name='report-count'),
    path('report-cws/', ReportCWs.as_view(), name='report-cws'),
    path('report-summary/', ReportSummary.as_view(), name='report-summary'),
    path('related-reports/', RelatedReports.as_view(), name='related-reports'),
    path('form-letters/', FormLettersIndex.as_view(), name='form-letters'),
    path('response-action/', ResponseAction.as_view(), name='response-action'),
    path('proform-attachment-action/', ProformAttachmentView.as_view(), name='proform-attachment-action'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
