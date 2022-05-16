from cts_forms.models import Report, ResponseTemplate
from rest_framework import serializers


class ReportSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api:report-detail',
    )

    class Meta:
        model = Report
        fields = ['url', 'pk', 'viewed']


class ResponseTemplateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api:response-detail',
    )

    class Meta:
        model = ResponseTemplate
        fields = ['url', 'pk', 'title', 'subject', 'body', 'language', 'is_html']

class RelatedReportSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api:report-detail',
    )

    class Meta:
        model = Report
        fields = ['url', 'pk', 'viewed', 'public_id', 'assigned_section', 'recent_email_sent', 'create_date', 'contact_email']