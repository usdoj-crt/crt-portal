from django.urls import path

from .views import (ActionsView, SavedSearchActionView, SavedSearchView, data_piecemeal_view, index_view, data_view, dashboard_view, dashboard_activity_log_view, disposition_view, RoutingGuideView, DispositionGuideView, DispositionActionsView, DispositionBatchActionsView, ShowView, ProFormView,
                    SaveCommentView, TrendView, ResponseView, SearchHelperView,
                    PrintView, ProfileView, ReportAttachmentView, ReportDataView, DataExport, RemoveReportAttachmentView, unsubscribe_view, notification_view, phone_pro_form_view)
from .forms import ProForm

app_name = 'crt_forms'


urlpatterns = [
    path('view/<int:id>/', ShowView.as_view(), name='crt-forms-show'),
    path('view/<int:id>/response', ResponseView.as_view(), name='crt-forms-response'),
    path('view/<int:id>/routing-guide/', RoutingGuideView.as_view(), name='routing-guide'),
    path('view/<int:id>/disposition-guide/', DispositionGuideView.as_view(), name='disposition-guide'),
    path('view/<int:id>/print', PrintView.as_view(), name='crt-forms-print'),
    path('view/<int:id>/attachments/<int:attachment_id>', ReportAttachmentView.as_view(), name='get-report-attachment'),
    path('view/reportsData/<int:report_data_id>', ReportDataView.as_view(), name='get-report-data'),
    path('data-export/', DataExport.as_view(), name='get-report-data'),
    path('view/', index_view, name='crt-forms-index'),
    path('view/update-profile', ProfileView.as_view(), name='cts-forms-profile'),
    path('view/search-examples', SearchHelperView.as_view(), name='cts-forms-search-help'),
    path('new/', ProFormView.as_view([ProForm]), name='crt-pro-form'),
    path('new/phone/', phone_pro_form_view, name='crt-pro-form'),
    path('actions/', ActionsView.as_view(), name='crt-forms-actions'),
    path('actions/print', PrintView.as_view(), name='crt-forms-print'),
    path('comment/report/<int:report_id>/', SaveCommentView.as_view(), name='save-report-comment'),
    path('attachment/report/<int:report_id>/', ReportAttachmentView.as_view(), name='save-report-attachment'),
    path('attachment/<int:attachment_id>/', RemoveReportAttachmentView.as_view(), name='remove-report-attachment'),
    path('trends/', TrendView.as_view(), name='trends'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('data/', data_view, name='data'),
    path('saved-searches/', SavedSearchView.as_view(), name='saved-searches'),
    path('saved-searches/actions/<int:id>/', SavedSearchActionView.as_view(), name='saved-search-actions'),
    path('saved-searches/actions/new', SavedSearchActionView.as_view(), name='saved-search-actions'),
    path('data/<str:notebook_names>/', data_piecemeal_view, name='data-piecemeal'),
    path('dashboard/activity', dashboard_activity_log_view, name='activity-log'),
    path('disposition', disposition_view, name='disposition'),
    path('disposition/actions', DispositionActionsView.as_view(), name='disposition-actions'),
    path('disposition/batch/<uuid:id>/', DispositionBatchActionsView.as_view(), name='disposition-batch-actions'),
    path('notifications/unsubscribe', unsubscribe_view, name='crt-forms-notifications-unsubscribe'),
    path('notifications/', notification_view, name='crt-forms-notifications'),
]
