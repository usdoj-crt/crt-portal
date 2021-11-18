import json
import logging
import re
from datetime import datetime, timezone
from urllib.parse import unquote

from cts_forms.models import DoNotEmail
from cts_forms.signals import get_client_ip
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import DisallowedHost
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from netaddr import IPNetwork

from .api.client import TMSClient
from .models import TMSEmail

logger = logging.getLogger(__name__)


class UnsubscribeView(View):
    """
    If UUID matches one we've generated for a sent email
    add the associated email to our DoNotEmail list
    """
    http_method_names = ['get']

    def get(self, request, pk):
        email = get_object_or_404(TMSEmail, id=pk)
        DoNotEmail.objects.get_or_create(recipient=email.recipient)
        return super().get(request, pk)


def _get_message_id(request):
    """
    return message ID integer from TMS provided message url
    https://stage-tms.govdelivery.com/messages/email/<message_id:int>
    """
    message_url = unquote(request.POST.get('message_url', ''))
    message_id = re.search(r'\d+', message_url)
    return message_id.group() if message_id else None


def _get_completed_at(request):
    """return a UTC datetime from inbound completed_at string, we're only expecting UTC
    e.g: "2015-08-05 18:47:18 UTC"
    """
    completed_at = unquote(request.POST.get('completed_at', ''))
    completed_datetime = datetime.strptime(completed_at, '%Y-%m-%d %H:%M:%S %Z').replace(tzinfo=timezone.utc)
    return completed_datetime


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """Handle inbound webhook requests from TMS"""

    http_method_names = ['post']

    def limit_by_origin(self, request):
        """
        True if the inbound request comes from an allowed origin
        We're using `netaddr` here to turn our configuredCIDR notation strings
        into python objects so that we can easily test for membership
        """
        # We're allowing all if explicitly configured
        if settings.TMS_WEBHOOK_ALLOWED_CIDR_NETS == ['*']:
            return True

        allowed_cidr_nets = [IPNetwork(net) for net in settings.TMS_WEBHOOK_ALLOWED_CIDR_NETS]
        ip = get_client_ip(request)

        for net in allowed_cidr_nets:
            if ip in net:
                return True
        raise DisallowedHost("Unexpected origin for a webhook request")

    def post(self, request):
        """Update TMSEmail instance of associated inbound webhook update"""
        self.limit_by_origin(request)
        message_id = _get_message_id(request)
        if message_id:
            try:
                email = TMSEmail.objects.get(tms_id=message_id)
            except TMSEmail.DoesNotExist:
                return HttpResponse(status=404)
            email.status = request.POST['status']
            email.completed_at = _get_completed_at(request)
            if email.failed:
                email.error_message = request.POST['error_message']
            email.save()
            logger.debug("Webhook update received and processed for TMS_ID: {message_id}")
            return HttpResponse(status=204)
        else:
            # We couldn't find a message ID in this request, do nothing and return 400
            return HttpResponse(status=400)


class AdminWebhookView(LoginRequiredMixin, View):
    """View webhook settings at TMS"""

    http_method_names = ['get']
    WEBHOOK_ENDPOINT = "/webhooks"

    @method_decorator(staff_member_required)
    def get(self, request):
        try:
            connection = TMSClient()
        # Raised when there are no TMS credentials in the env
        except AttributeError:
            return render(request, 'email.html', {'data': 'no tms settings here'})

        response = connection.get(target=self.WEBHOOK_ENDPOINT)
        parsed = json.loads(response.content)
        return render(request, 'email.html', {'data': json.dumps(parsed, indent=2)})


class AdminMessageView(LoginRequiredMixin, View):
    """View message status at TMS"""

    http_method_names = ['get']
    WEBHOOK_ENDPOINT = "/messages/email"

    @method_decorator(staff_member_required)
    def get(self, request, tms_id):
        if not tms_id:
            return render(request, 'email.html', {'data': 'need an email id'})

        try:
            connection = TMSClient()
        # Raised when there are no TMS credentials in the env
        except AttributeError:
            return render(request, 'email.html', {'data': 'no tms settings here'})

        response = connection.get(target=self.WEBHOOK_ENDPOINT + '/' + str(tms_id))
        parsed = json.loads(response.content)

        if parsed.status == 'completed':
            if parsed.recipient_counts.failed > 0:
                response2 = connection.get(target=parsed._links.failed)
                parsed2 = json.loads(response2.content)
            elif parsed.recipient_counts.sent > 0:
                response2 = connection.get(target=parsed._links.sent)
                parsed2 = json.loads(response2.content)

            return render(request, 'email.html', {'data': json.dumps(parsed, indent=2) + '\n' + json.dumps(parsed2, indent=2)})
        else:
            return render(request, 'email.html', {'data': json.dumps(parsed, indent=2)})
