from django.contrib.auth.models import User
from cts_forms.models import Report, ResponseTemplate
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from cts_forms.views import mark_report_as_viewed

from api.serializers import UserSerializer, ReportSerializer, ResponseTemplateSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'reports': reverse('report-list', request=request, format=format),
        'responses': reverse('response-list', request=request, format=format)
    })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ReportList(generics.ListAPIView):
    """
    API endpoint that allows Reports to be viewed.
    """
    queryset = Report.objects.all().order_by('pk')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportDetail(generics.RetrieveUpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
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
