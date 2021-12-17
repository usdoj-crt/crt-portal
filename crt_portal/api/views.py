from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.contrib.auth.models import User
from cts_forms.models import Report, ResponseTemplate
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers import UserSerializer, ReportSerializer, ResponseTemplateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResponseTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ResponseTemplate.objects.all()
    serializer_class = ResponseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Report.objects.all().order_by('pk')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportList(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request, format=None):
        snippets = Report.objects.all()
        serializer = ReportSerializer(snippets, many=True)
        return Response(serializer.data)


def report_opened(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    print("request", request)
    print("in report_opened")
    # try:
    #     report = Report.objects.get(pk=pk)
    # except Report.DoesNotExist:
    #     return HttpResponse(status=404)
    #
    # if request.method == 'GET':
    #     data = JSONParser().parse(request)
    #     print("data", data)
    #     serializer = ReportSerializer(report)
    #     return JsonResponse(serializer.data)
    #
    # elif request.method == 'PUT':
    #     data = JSONParser().parse(request)
    #     serializer = ReportSerializer(report, data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return JsonResponse(serializer.data)
    #     return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
