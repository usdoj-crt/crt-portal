from api.filters import form_letters_filter, reports_accessed_filter, autoresponses_filter, report_cws
from django.utils.html import mark_safe
from api.serializers import ReportSerializer, ResponseTemplateSerializer, RelatedReportSerializer
from cts_forms.filters import report_filter
from cts_forms.mail import CustomHTMLExtension
from cts_forms.models import Report, ResponseTemplate
from cts_forms.views import mark_report_as_viewed, mark_reports_as_viewed
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import frontmatter
import html
import json
import markdown
import os

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
        'report-cws': reverse('api:report-cws', request=request, format=format)
    })


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
        base_context = {
            'addressee': self._mark_variable('Addressee Name'),
            'contact_address_line_1': self._mark_variable('Contact Address Line 1'),
            'contact_address_line_2': self._mark_variable('Contact Address Line 2'),
            'contact_email': self._mark_variable('Contact Email'),
            'date_of_intake': self._mark_variable('Date of Intake'),
            'outgoing_date': self._mark_variable('Outgoing Date'),
            'section_name': self._mark_variable('Section'),
        }

        lang_contexts = {
            lang: {
                key: f'[{lang}] {value}'
                for key, value in base_context.items()
            } for lang in ['es', 'ko', 'tl', 'vi', 'zh_hans', 'zh_hant']
        }

        return Context({
            'record_locator': self._mark_variable('Record Locator'),
            **base_context,
            **lang_contexts,
        })

    def _add_css(self, body):
        return body + mark_safe(
            '{% load static %}'
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
            md = markdown.markdown(subbed, extensions=['extra', 'nl2br', CustomHTMLExtension(), *extra_markdown_extensions])
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
        if report_pk:
            report = Report.objects.filter(pk=report_pk).first()
            serialized_data['url'] = serialized_data['url'] + '?report_id=' + report_pk
            serialized_data['subject'] = template.render_subject(report)
            serialized_data['body'] = html.unescape(template.render_body(report))
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
