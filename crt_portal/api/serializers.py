from cts_forms.models import Report, ResponseTemplate
from rest_framework import serializers


class ReportSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api:report-detail',
    )

    class Meta:
        model = Report
        fields = ['url', 'pk', 'viewed']

class ResponseTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResponseTemplate
        fields = ['title', 'subject', 'body', 'language']