"""crt_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from cts_forms.forms import (
    Contact,
    Details,
    PrimaryReason,
    LocationForm,
    ProtectedClassForm,
    ElectionLocation,
    WorkplaceLocation,
    PoliceLocation,
    CommercialPublicLocation,
    EducationLocation,
    When,
)
from cts_forms.views import (
    CRTReportWizard,
    show_election_form_condition,
    show_location_form_condition,
    show_workplace_form_condition,
    show_police_form_condition,
    show_education_form_condition,
    show_commercial_public_form_condition,
)


environment = os.environ.get('ENV', 'UNDEFINED')
if environment == 'PRODUCTION':
    auth = [
        re_path('admin/login/$', RedirectView.as_view(pattern_name='oauth2/', permanent=False)),
        re_path('accounts/login/$', RedirectView.as_view(pattern_name='oauth2/', permanent=False)),
        path('oauth2/', include('django_auth_adfs.urls')),
    ]
else:
    auth = []

# add app related urls here or in cts_forms.urls
urlpatterns = auth + [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/', include('cts_forms.urls')),
    path('report/', CRTReportWizard.as_view(
        [
            Contact,
            PrimaryReason,
            ElectionLocation,
            WorkplaceLocation,
            PoliceLocation,
            CommercialPublicLocation,
            EducationLocation,
            LocationForm,
            ProtectedClassForm,
            When,
            Details,
        ],
        condition_dict={
            '2': show_election_form_condition,
            '3': show_workplace_form_condition,
            '4': show_police_form_condition,
            '5': show_commercial_public_form_condition,
            '6': show_education_form_condition,
            '7': show_location_form_condition,
        },
    ), name='crt_report_form'),
    path('', RedirectView.as_view(pattern_name='crt_report_form', permanent=False)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
