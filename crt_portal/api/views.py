import logging
import mimetypes
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from api.filters import form_letters_filter, reports_accessed_filter, autoresponses_filter, report_cws
from django.utils.html import mark_safe
from api.serializers import ReportSerializer, ResponseTemplateSerializer, RelatedReportSerializer
from utils.pdf import convert_html_to_pdf
from cts_forms.filters import report_filter
from cts_forms.mail import mail_to_complainant, mail_to_agency, build_letters, build_preview
from utils.markdown_extensions import CustomHTMLExtension, OptionalExtension
from cts_forms.models import Report, ResponseTemplate, ReportAttachment
from cts_forms.views import mark_report_as_viewed, mark_reports_as_viewed
from cts_forms.forms import add_activity, ProformAttachmentActions
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template import Context, Template
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from django.http import Http404
import frontmatter
import base64
import json
import markdown
import os
from urllib.parse import unquote

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


@api_view(['GET'])
@login_required
def api_root(request, format=None):
    return Response({
        'reports': reverse('api:report-list', request=request, format=format),
        'responses': reverse('api:response-list', request=request, format=format),
        'report-count': reverse('api:report-count', request=request, format=format),
        'related-reports': reverse('api:related-reports', request=request, format=format),
        'form-letters': reverse('api:form-letters', request=request, format=format),
        'report-cws': reverse('api:report-cws', request=request, format=format),
        'response-action': reverse('api:response-action', request=request, format=format),
        'proform-attachment-action': reverse('api:proform-attachment-action', request=request, format=format)
    })


def upload_file(attachment):
    if settings.ENABLE_LOCAL_ATTACHMENT_STORAGE:
        try:
            file = open(attachment.file.name, 'rb')
            mime_type, _ = mimetypes.guess_type(attachment.filename)
            response = HttpResponse(file, content_type=mime_type)
            response.headers['Content-Disposition'] = f'attachment;filename={attachment.filename}'
            return response

        except FileNotFoundError:
            raise Http404(f'File {attachment.filename} not found.')

    else:
        # Generate a presigned URL for the S3 object
        s3_client = boto3.client(
            service_name='s3',
            region_name=settings.PRIV_S3_REGION,
            aws_access_key_id=settings.PRIV_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.PRIV_S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.PRIV_S3_ENDPOINT_URL,
            config=Config(signature_version='s3v4'))

        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.PRIV_S3_BUCKET,
                    'Key': attachment.file.name,
                    'ResponseContentDisposition': f'attachment;filename={attachment.filename}'
                },
                ExpiresIn=30,
            )

            return response

        except ClientError as e:
            logging.error(e)
            raise Http404(f'File {attachment.filename} not found.')


class ReportList(generics.ListAPIView):
    """
    API endpoint that allows Reports to be viewed.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Report.objects.all().order_by('pk')
    serializer_class = ReportSerializer

    def post(self, request, *args, **kwargs):
        try:
            report_pks = request.data['report_pks']
        except (json.decoder.JSONDecodeError, KeyError):
            return HttpResponse(status=400)

        reports = Report.objects.filter(pk__in=report_pks).all()
        mark_reports_as_viewed(reports, request.user)
        return HttpResponse(status=200)


class ReportCountView(APIView):
    """
    A view that returns the count of reports matching given filters.


    Example: api/report/?start_date=2022-02-01&end_date=2022-04-14&intake_specialist=USER_1
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        reports_accessed_payload = reports_accessed_filter(request.GET)
        return Response(reports_accessed_payload)


class ReportDetail(generics.RetrieveUpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        report_pk = kwargs.get("pk")
        if report_pk:
            report = Report.objects.filter(pk=report_pk).first()
            mark_report_as_viewed(report, request.user)
        return self.update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        report_pk = kwargs.get("pk")
        if report_pk:
            report = Report.objects.filter(pk=report_pk).first()
            mark_report_as_viewed(report, request.user)
        return self.update(request, *args, **kwargs)


class ResponseTemplatePreviewBase:
    _templates_dir = os.path.join(settings.BASE_DIR, 'cts_forms', 'response_templates')

    def _mark_variable(self, value):
        return mark_safe(f'<span class="variable">{value}</span>')

    def _make_example_context(self):
        to_be_translated = {
            'addressee': 'Addressee Name',
            'date_of_intake': 'Date of Intake',
            'outgoing_date': 'Outgoing Date',
            'section_name': 'Section',
        }

        lang_contexts = {
            lang: {
                key: self._mark_variable(f'[{lang}] {value}')
                for key, value in to_be_translated.items()
            } for lang in ['es', 'ko', 'tl', 'vi', 'zh_hans', 'zh_hant']
        }

        return Context({
            # The following are 'en' only.
            'contact_address_line_1': self._mark_variable('Contact Address Line 1'),
            'contact_address_line_2': self._mark_variable('Contact Address Line 2'),
            'contact_email': self._mark_variable('Contact Email'),
            'referral_text': self._mark_variable('Referral Text'),
            'record_locator': self._mark_variable('Record Locator'),
            **{k: self._mark_variable(v) for k, v in to_be_translated.items()},
            **lang_contexts,
        })

    def _add_css(self, body):
        return body + mark_safe(
            '<link rel="stylesheet" href="{% static "css/compiled/template-preview.css" %}">'
        )

    def _render_response_template(self, request, *, is_html=False, body='', extra_markdown_extensions=None, **kwargs):
        if extra_markdown_extensions is None:
            extra_markdown_extensions = []
        if isinstance(body, list):
            body = ''.join(body)
        body = self._add_css(body)
        del kwargs  # Allow for extra, unused render variables.
        context = self._make_example_context()
        if is_html:
            subbed = str(Template(body).render(context))
            md = markdown.markdown(subbed, extensions=[OptionalExtension(preview=True), 'extra', 'sane_lists', 'admonition', 'nl2br', CustomHTMLExtension(), *extra_markdown_extensions])
            return render(request, 'email.html', {'content': md})

        return HttpResponse(Template(body.replace('\n', '<br>')).render(context))


class ResponseTemplateFormPreview(generics.ListAPIView, ResponseTemplatePreviewBase):
    """API endpoint that allows responses to be viewed based on content."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        help_path = os.path.join(settings.BASE_DIR, 'cts_forms/templates/template_help.md')

        with open(help_path, 'r') as f:
            content = frontmatter.load(f)

        return self._render_response_template(
            request,
            is_html=True,
            body=str(content),
            extra_markdown_extensions=['toc'])

    def post(self, request):
        return self._render_response_template(request, **request.data)


class ResponseTemplateFilePreview(generics.ListAPIView, ResponseTemplatePreviewBase):
    """API endpoint that allows responses to be viewed given a filename."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, filename):
        if not filename:
            return HttpResponse('No filename provided', status=400)

        path = os.path.join(self._templates_dir, filename)
        with open(path, 'r') as f:
            content = frontmatter.load(f)

        return self._render_response_template(
            request,
            is_html=content.get('is_html', False),
            body=str(content))


class ResponseList(generics.ListAPIView):
    """
    API endpoint that allows responses to be viewed.
    """
    queryset = ResponseTemplate.objects.all()
    serializer_class = ResponseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResponseDetail(generics.RetrieveAPIView):
    queryset = ResponseTemplate.objects.all()
    serializer_class = ResponseTemplateSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = self.get_serializer(template)
        # Makes a copy of the serialized data so it can be updated
        serialized_data = serializer.data
        # If a `?report_id=<pk>` is provided, then render the letter content
        # with the given report details
        report_pk = request.query_params.get('report_id')
        if not report_pk:
            return Response(serialized_data)

        optionals = request.query_params.get('optionals')
        if optionals:
            optionals = json.loads(unquote(optionals))

        report = Report.objects.filter(pk=report_pk).first()
        serialized_data['url'] = serialized_data['url'] + '?report_id=' + report_pk
        serialized_data['subject'] = template.render_subject(report)
        serialized_data['body'] = template.render_body_as_markdown(report, optionals=optionals)
        serialized_data['optionals'] = template.get_optionals()

        return Response(serialized_data)


class ReportSummary(APIView):
    """
    A view that returns counts of reports matching filters.


    Example: api/report-summary/?violation_summary=some%20summary
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        filtered, _ = report_filter(request.GET)
        return Response({"report_count": filtered.count()})


class ReportCWs(APIView):
    """
    A view that returns a boolean of whether the email associated with a report has been sent the constant writer email accessed in JSON.
    Example: api/report-cws/
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        report_cws_payload = report_cws(request.data)
        return Response(report_cws_payload)


class RelatedReports(generics.ListAPIView):
    """
    A view that lists all of the reports filed using the same email address.


    Example: api/related-reports/?email=test.test@test.com
    """

    permission_classes = (IsAuthenticated,)
    queryset = Report.objects.all().exclude(contact_email__isnull=True)
    serializer_class = RelatedReportSerializer

    def get_queryset(self):
        email_address = self.request.query_params.get('email')
        reports = self.queryset.filter(contact_email__iexact=email_address).order_by('status', '-create_date')
        return reports


class FormLettersIndex(APIView):
    """
    A view that displays information about the number of form letters sent.


    Example: /api/form-letters/?assigned_section=CRM&start_date=2022-03-24&end_date=2022-03-29
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            form_letters_payload = form_letters_filter(request.GET)
            total_autoresponses = autoresponses_filter(request.GET)
            form_letters_payload["total_autoresponses"] = total_autoresponses
            return Response(form_letters_payload)
        except ValueError:
            return HttpResponse(status=400)
        except IndexError:
            return HttpResponse(status=500)


class ResponseAction(APIView):
    """
    API endpoint that enables referral letter previews and email send status


    Example: api/response-action/
    """

    permission_classes = (IsAuthenticated,)

    MAIL_SERVICE = "govDelivery TMS"

    def post(self, request) -> JsonResponse:
        report_id = request.data.get('report_id')
        if report_id is None:
            return JsonResponse({'response': 'Referral email failed to send: No report id provided!'}, status=400)
        report = get_object_or_404(Report, pk=report_id)
        template_id = request.data.get('template_id')
        if template_id is None:
            return JsonResponse({'response': 'Referral email failed to send: No template id provided!'}, status=400)
        template = get_object_or_404(ResponseTemplate, pk=template_id)
        action = request.data['action']
        recipient = request.data.get('recipient', None)
        complainant_letter, agency_letter = build_letters(
            report,
            template,
            action=action,
        )

        if action == 'preview':
            preview = build_preview(template, complainant_letter, agency_letter)
            return JsonResponse(preview)

        if action == 'print':
            return self._print_mail(request=request,
                                    report=report,
                                    template=template,
                                    recipient=recipient,
                                    complainant_letter=complainant_letter,
                                    agency_letter=agency_letter)

        if action != 'send':
            return JsonResponse({
                'response': (
                    f'Referral email template #{template.pk} failed to send '
                    'to report #{report.pk}: Action "{action}" is not supported'
                )}, status=400)

        return self._send_mail(request=request,
                               report=report,
                               template=template,
                               recipient=recipient,
                               complainant_letter=complainant_letter,
                               agency_letter=agency_letter)

    def _print_mail(self, *, request, report, template, recipient,
                    complainant_letter, agency_letter) -> JsonResponse:
        action = 'Printed' if recipient == 'complainant' else 'Printed referral'
        description = f"{action} '{template.title}' template"
        add_activity(request.user,
                     f"Contacted {recipient}:",
                     description,
                     report)
        message = (
            complainant_letter.html_message
            if recipient == 'complainant'
            else agency_letter.html_message
        )
        pdfBytes = convert_html_to_pdf(message).getvalue()
        return JsonResponse({
            'response': description,
            'pdf': base64.b64encode(pdfBytes).decode('utf-8'),
        })

    def _send_mail(self, *, request, report, template, recipient,
                   complainant_letter, agency_letter) -> JsonResponse:
        if not recipient or recipient not in ['agency', 'complainant']:
            return JsonResponse({'response': f'Referral email template #{template.pk} failed to send to report #{report.pk}: A recipient ("agency" or "complainant") must be specified.'}, status=400)

        try:
            if recipient == 'complainant':
                email_response = mail_to_complainant(report, template, rendered=complainant_letter)
            else:
                email_response = mail_to_agency(report, template, rendered=agency_letter)
        except Exception as e:
            return JsonResponse({'response': f'Referral email template #{template.pk} failed to send to report #{report.pk}: {e}'}, status=502)

        if not email_response:
            description = f"{report.contact_email} not in allowed domains, not attempting to deliver {template.title}."
            add_activity(request.user, f"Contacted {recipient}:", description, report)
            return JsonResponse({'response': description}, status=502)

        addressee = report.contact_email if recipient == 'complainant' else template.referral_contact.name
        action = 'Email sent' if recipient == 'complainant' else 'Referral sent'
        description = f"{action}: '{template.title}' to {addressee} via {self.MAIL_SERVICE}"
        add_activity(request.user, f"Contacted {recipient}:", description, report)
        return JsonResponse({'response': description})


class ProformAttachmentView(APIView):
    """
    API endpoint that enables adding attachments to the proform


    Example: api/proform-attachment-action/
    """
    form_class = ProformAttachmentActions
    permission_classes = (IsAuthenticated,)

    def post(self, request) -> JsonResponse:
        action = request.POST.get('action')
        if action == 'removed':
            try:
                attachment_id = int(request.POST.get('attachment_id'))
                attachment = get_object_or_404(ReportAttachment, pk=attachment_id)
                name = attachment.filename
                attachment.delete()
                return JsonResponse({'response': f'File {name} was successfully {action}', 'id': attachment_id, 'name': name, 'type': 'success'})
            except ValueError:
                return HttpResponse(status=400)
        attachment_form = self.form_class(request.POST, request.FILES)
        if attachment_form.is_valid() and attachment_form.has_changed():
            attachment = attachment_form.save(commit=False)
            name = attachment.filename
            attachment.save()
            attachment_id = attachment.pk
            return JsonResponse({'response': f'File {name} was successfully {action}', 'id': attachment_id, 'name': name, 'type': 'success'})
        else:
            errors = [value for _, value in attachment_form.errors.items()]
            error_message = f'Could not save attachment: {errors}'
            return JsonResponse({'response': error_message, 'type': 'error'})

    def get(self, request) -> JsonResponse:
        """
        Download a particular attachment for a report
        """
        attachment_id = int(request.GET['attachment_id'])
        attachment = get_object_or_404(ReportAttachment, pk=attachment_id)
        return upload_file(attachment)
