from django.http import HttpResponse
from cts_forms.models import Report, ResponseTemplate
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from cts_forms.views import mark_report_as_viewed
from api.filters import form_letters_filter, reports_accessed_filter, autoresponses_filter
from rest_framework.permissions import IsAuthenticated
from api.serializers import ReportSerializer, ResponseTemplateSerializer, RelatedReportSerializer
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
import html

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
        'form-letters': reverse('api:form-letters', request=request, format=format)
    })


class ReportList(generics.ListAPIView):
    """
    API endpoint that allows Reports to be viewed.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Report.objects.all().order_by('pk')
    serializer_class = ReportSerializer


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
            if not report.viewed:
                mark_report_as_viewed(report, request.user)
        return self.update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        report_pk = kwargs.get("pk")
        if report_pk:
            report = Report.objects.filter(pk=report_pk).first()
            if not report.viewed:
                mark_report_as_viewed(report, request.user)
        return self.update(request, *args, **kwargs)


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


class ReportCountView(APIView):
    """
    A view that returns the count of reports accessed in JSON.


    Example: api/report-count/?start_date=2022-02-01&end_date=2022-04-14&intake_specialist=USER_1
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        reports_accessed_payload = reports_accessed_filter(request.GET)
        return Response(reports_accessed_payload)


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
