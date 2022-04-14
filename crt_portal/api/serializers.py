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


class FormLetterSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, allow_blank=True, max_length=100)
    class Meta:
        fields = ['title']