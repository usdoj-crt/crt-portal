from django.urls import path

from .views import UnsubscribeView, WebhookView

app_name = 'tms'

urlpatterns = [
    path('unsubscribe/<uuid:pk>/', UnsubscribeView.as_view(), name='email-unsubscribe'),
    path('webhook/', WebhookView.as_view(), name='tms-webhook'),
]
