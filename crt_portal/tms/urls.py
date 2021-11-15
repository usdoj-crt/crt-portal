from django.urls import path

from .views import UnsubscribeView, WebhookView, AdminWebhookView, AdminMessageView

app_name = 'tms'

urlpatterns = [
    path('unsubscribe/<uuid:pk>/', UnsubscribeView.as_view(), name='email-unsubscribe'),
    path('webhook/', WebhookView.as_view(), name='tms-webhook'),
    path('admin/', AdminWebhookView.as_view(), name='tms-admin-webhook'),
    path('admin/webhooks/', AdminWebhookView.as_view(), name='tms-admin-webhook'),
    path('admin/messages/<int:tms_id>/', AdminMessageView.as_view(), name='tms-admin-message'),
]
