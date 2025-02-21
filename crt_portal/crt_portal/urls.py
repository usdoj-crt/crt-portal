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

from cts_forms.forms import (
    CommercialPublicLocation, Contact, Details,
    EducationLocation, ElectionLocation,
    LocationForm, PoliceLocation, PrimaryReason,
    ProtectedClassForm, Review, When,
    WorkplaceLocation
)
from cts_forms.views_public import (
    CRTReportWizard, LandingPageView, error_404, error_422, error_500,
    show_commercial_public_form_condition,
    show_education_form_condition,
    show_election_form_condition,
    show_location_form_condition,
    show_police_form_condition,
    show_workplace_form_condition,
    printable_form_view
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from mozilla_django_oidc import views as oidc_views

environment = os.environ.get('ENV', 'UNDEFINED')
if environment in ['PRODUCTION', 'STAGE']:
    auth = [
        # ADFS
        path('oauth2/', include('django_auth_adfs.urls')),

        # OKTA
        path("authorization-code/authenticate/", oidc_views.OIDCAuthenticationRequestView.as_view(), name="oidc_authentication_init"),
        path("authorization-code/callback/", oidc_views.OIDCAuthenticationCallbackView.as_view(), name="oidc_authentication_callback")
    ]
else:
    auth = []


def redirect_static(request):
    target = request.path.replace('/static/', settings.STATIC_URL)
    return redirect(target)


static_for_aws = [
    re_path(r'^static/.*$', redirect_static, name='aws-static-redirect')
]

if settings.STATIC_URL == '/static/':
    static_urls = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    static_urls = static_for_aws

# add app related urls here or in cts_forms.urls
urlpatterns = auth + [
    path("oauth2_provider/", include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('email/', include('tms.urls')),
    path('form/', include('cts_forms.urls')),
    path('link/', include('shortener.urls')),
    path('analytics/', include('analytics.urls')),
    path('report/printable/', printable_form_view, name='printable-form'),
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
            Review,
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
    path('privacy-policy', TemplateView.as_view(template_name="privacy.html"), name='privacy_policy'),
    path('hate-crime-human-trafficking', TemplateView.as_view(template_name="hate_crime_human_trafficking.html"), name='hate_crime_human_trafficking'),
    path('housing-resources', TemplateView.as_view(template_name="hce_resources.html"), name='hce_resources'),
    path('voting-resources', TemplateView.as_view(template_name="vot_resources.html"), name='vot_resources'),
    path('', LandingPageView.as_view(), name='crt_landing_page'),
    path('api/', include('api.urls')),
] + static_urls

handler400 = 'cts_forms.views_public.error_400'
handler403 = 'cts_forms.views_public.error_403'
handler404 = 'cts_forms.views_public.error_404'
handler500 = 'cts_forms.views_public.error_500'
handler501 = 'cts_forms.views_public.error_501'
handler502 = 'cts_forms.views_public.error_502'
handler503 = 'cts_forms.views_public.error_503'

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if settings.DEBUG:
    urlpatterns += [
        path('errors/404', error_404),
        path('errors/422', error_422),
        path('errors/500', error_500),
    ]
