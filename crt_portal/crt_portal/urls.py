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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
import django_saml2_auth.views

from cts_forms.forms import Contact, Details, PrimaryReason, ProtectedClassForm
from cts_forms.views import CRTReportWizard

environment = os.environ.get('ENV', 'PROD')

# Turning this off on local development for now
if environment != 'LOCAL':
    # These are the SAML2 related URLs. You can change "^saml2_auth/" regex to
    # any path you want, like "^sso_auth/", "^sso_login/", etc. (required)
    path('saml2_auth/', include('django_saml2_auth.urls')),

    # The following line will replace the default user login with SAML2 (optional)
    # If you want to specific the after-login-redirect-URL, use parameter "?next=/the/path/you/want"
    # with this view.
    path('accounts/login/', django_saml2_auth.views.signin),

    # The following line will replace the admin login with SAML2 (optional)
    # If you want to specific the after-login-redirect-URL, use parameter "?next=/the/path/you/want"
    # with this view.
    path('admin/login/', django_saml2_auth.views.signin),

    # The following line will replace the default user logout with the signout page (optional)
    path('accounts/logout/', django_saml2_auth.views.signout),

    # The following line will replace the default admin user logout with the signout page (optional)
    path('admin/logout/', django_saml2_auth.views.signout),


# add app related urls here or in cts_forms.urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('form/', include('cts_forms.urls')),
    path('report/', CRTReportWizard.as_view([
        Contact,
        PrimaryReason,
        ProtectedClassForm,
        Details,
        # WhatHappened,
        # Where,
        # Who,
    ]), name='crt_report_form'),
    path('', RedirectView.as_view(pattern_name='crt_report_form', permanent=False)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
