from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import UserViewSet, ResponseList, ReportList, ReportDetail, api_root

user_list = UserViewSet.as_view({
    'get': 'list'
})
user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    path('', api_root),
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('responses/', ResponseList.as_view(), name='response-list'),
    path('reports/', ReportList.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetail.as_view(), name='report-detail'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
