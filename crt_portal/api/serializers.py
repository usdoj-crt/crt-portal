from django.contrib.auth.models import User
from cts_forms.models import Report, ResponseTemplate
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    print("report serializer")

    class Meta:
        model = Report
        fields = ['pk', 'read']


class ResponseTemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResponseTemplate
        fields = ['title', 'subject', 'body', 'language']
