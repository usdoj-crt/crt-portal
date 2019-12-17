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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from cts_forms.forms import Contact, Details, PrimaryReason, LocationForm, ProtectedClassForm, ElectionLocation
from cts_forms.views import CRTReportWizard, show_election_form_condition, show_location_form_condition

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/', include('cts_forms.urls')),
    path('report/', CRTReportWizard.as_view(
        [
            Contact,
            PrimaryReason,
            ElectionLocation,
            LocationForm,
            ProtectedClassForm,
            Details,
        ],
        condition_dict={
            '2': show_election_form_condition,
            '3': show_location_form_condition,
        },
    ), name='crt_report_form'),
    path('', RedirectView.as_view(pattern_name='crt_report_form', permanent=False)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
