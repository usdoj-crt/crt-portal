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
from django.views.generic import RedirectView, TemplateView

from cts_forms.forms import (
    Contact,
    Details,
    PrimaryReason,
    HateCrimesTrafficking,
    LocationForm,
    ProtectedClassForm,
    ElectionLocation,
    WorkplaceLocation,
    PoliceLocation,
    CommercialPublicLocation,
    EducationLocation,
    When,
    Review,
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
        re_path('admin/login/$', RedirectView.as_view(pattern_name='login')),
        re_path('accounts/login/$', RedirectView.as_view(pattern_name='login')),
        path('oauth2/', include('django_auth_adfs.urls'), name='login'),
    ]
else:
    auth = []

# add app related urls here or in cts_forms.urls
urlpatterns = auth + [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    path('form/', include('cts_forms.urls')),
    path('report/', CRTReportWizard.as_view(
        [
            Contact,
            PrimaryReason,
            HateCrimesTrafficking,
            ElectionLocation,
            WorkplaceLocation,
            PoliceLocation,
            CommercialPublicLocation,
            EducationLocation,
            LocationForm,
            ProtectedClassForm,
            When,
            Details,
            Review,
        ],
        condition_dict={
            '3': show_election_form_condition,
            '4': show_workplace_form_condition,
            '5': show_police_form_condition,
            '6': show_commercial_public_form_condition,
            '7': show_education_form_condition,
            '8': show_location_form_condition,
        },
    ), name='crt_report_form'),
    path('', RedirectView.as_view(pattern_name='crt_report_form', permanent=False)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'cts_forms.views.error_400'
handler403 = 'cts_forms.views.error_403'
handler404 = 'cts_forms.views.error_404'
handler500 = 'cts_forms.views.error_500'
handler501 = 'cts_forms.views.error_501'
handler502 = 'cts_forms.views.error_502'
handler503 = 'cts_forms.views.error_503'
