from django.contrib.auth.models import User
from cts_forms.models import Report, ResponseTemplate
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = ['url', 'pk', 'viewed']


class ResponseTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResponseTemplate
        fields = ['title', 'subject', 'body', 'language']
