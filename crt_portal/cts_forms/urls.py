from django.urls import path

from .views import (ActionsView, index_view, data_view, dashboard_view, dashboard_activity_log_view, disposition_view, RoutingGuideView, ShowView, ProFormView,
                    SaveCommentView, TrendView, ResponseView, SearchHelperView,
                    PrintView, ProfileView, ReportAttachmentView, ReportDataView, DataExport, RemoveReportAttachmentView, unsubscribe_view)
from .forms import ProForm

app_name = 'crt_forms'


urlpatterns = [
    path('view/<int:id>/', ShowView.as_view(), name='crt-forms-show'),
    path('view/<int:id>/response', ResponseView.as_view(), name='crt-forms-response'),
    path('view/<int:id>/routing-guide/', RoutingGuideView.as_view(), name='routing-guide'),
    path('view/<int:id>/print', PrintView.as_view(), name='crt-forms-print'),
    path('view/<int:id>/attachments/<int:attachment_id>', ReportAttachmentView.as_view(), name='get-report-attachment'),
    path('view/reportsData/<int:report_data_id>', ReportDataView.as_view(), name='get-report-data'),
    path('data-export/', DataExport.as_view(), name='get-report-data'),
    path('view/', index_view, name='crt-forms-index'),
    path('view/update-profile', ProfileView.as_view(), name='cts-forms-profile'),
    path('view/search-examples', SearchHelperView.as_view(), name='cts-forms-search-help'),
    path('new/', ProFormView.as_view([ProForm]), name='crt-pro-form'),
    path('actions/', ActionsView.as_view(), name='crt-forms-actions'),
    path('actions/print', PrintView.as_view(), name='crt-forms-print'),
    path('comment/report/<int:report_id>/', SaveCommentView.as_view(), name='save-report-comment'),
    path('attachment/report/<int:report_id>/', ReportAttachmentView.as_view(), name='save-report-attachment'),
    path('attachment/<int:attachment_id>/', RemoveReportAttachmentView.as_view(), name='remove-report-attachment'),
    path('trends/', TrendView.as_view(), name='trends'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('data/', data_view, name='data'),
    path('dashboard/activity', dashboard_activity_log_view, name='activity-log'),
    path('disposition', disposition_view, name='disposition'),
    path('notifications/unsubscribe', unsubscribe_view, name='crt-forms-notifications-unsubscribe'),
]
