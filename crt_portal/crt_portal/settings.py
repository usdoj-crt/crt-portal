"""
Django settings for crt_portal project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import json
import os
import sys

import boto3
import django.conf.locale
from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import gettext_lazy as _

# Are we in a test environment?
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Note that when using Docker, ENV is set to "LOCAL" by docker-compose.yml. We are using Docker for local development only.
# We are running the testing environment with UNDEFINED.
# For cloud.gov the ENV must be set in the manifests
environment = os.environ.get('ENV', 'UNDEFINED')
USE_LOCALSTACK = os.environ.get('USE_LOCALSTACK', None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)
ENABLE_DEBUG_TOOLBAR = os.environ.get('ENABLE_DEBUG_TOOLBAR', False)
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', False)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

if environment != 'LOCAL':
    """ This will default to prod settings and locally, setting the env
    to local will allow you to add the variables directly and not have
    to recreate the vacap structure."""
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    for service in vcap['user-provided']:
        if service['instance_name'] == "VCAP_SERVICES":
            # SECURITY WARNING: keep the secret key used in production secret!
            SECRET_KEY = service['credentials']['SECRET_KEY']

    db_credentials = vcap['aws-rds'][0]['credentials']

    # Database
    # https://docs.djangoproject.com/en/2.2/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_credentials['db_name'],
            'USER': db_credentials['username'],
            'PASSWORD': db_credentials['password'],
            'HOST': db_credentials['host'],
            'PORT': '',
        }
    }

# production hosts are specified later
ALLOWED_HOSTS = [
    'crt-portal.app.cloud.gov',
    'crt-portal-django.app.cloud.gov',
    'crt-portal-django-stage.app.cloud.gov',
    'crt-portal-django-dev.app.cloud.gov',
]

if environment == 'UNDEFINED':
    ALLOWED_HOSTS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'actstream',
    'cts_forms',
    'compressor',
    'compressor_toolkit',
    'storages',
    'formtools',
    # 'django_auth_adfs' in production only
    'crequest',
    'tms'
]
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'crequest.middleware.CrequestMiddleware',
]

ROOT_URLCONF = 'crt_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': ['cts_forms.templatetags.with_input_error'],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crt_portal.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

TL_INFO = {
    'tl': {
        'bidi': True,
        'code': 'tl',
        'name': 'Tagalog',
        'name_local': 'Tagalog',
    }
}
LANG_INFO = dict(django.conf.locale.LANG_INFO, **TL_INFO)
django.conf.locale.LANG_INFO = LANG_INFO

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('es', _('Spanish')),
    ('en', _('English')),
    ('zh-hant', _('Chinese Traditional')),
    ('zh-hans', _('Chinese Simplified')),
    ('vi', _('Vietnamese')),
    ('ko', _('Korean')),
    ('tl', _('Tagalog')),
]

# Set LOCALE_PATHS to ensure that our translations are given precedence
# https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#how-django-discovers-translations
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'cts_forms', 'locale'),
]

# App use Easter Time, database use UTC
TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Set to True later in settings if we've successfully configured an email backend
EMAIL_ENABLED = False

TMS_WEBHOOK_ALLOWED_CIDR_NETS = os.environ.get('TMS_WEBHOOK_ALLOWED_CIDR_NETS', '').split(';')
TMS_STAGING_ENDPOINT = "https://stage-tms.govdelivery.com"
TMS_PRODUCTION_ENDPOINT = "https://tms.govdelivery.com"
# Since there's no sandbox, we'll limit outbound recipients to these addresses
# to avoid un-intentional emails
RESTRICT_EMAIL_RECIPIENTS_TO = os.environ.get('RESTRICT_EMAIL_RECIPIENTS_TO', '').split(';')

EMAIL_AUTORESPONSE_ENABLED = os.environ.get('EMAIL_AUTORESPONSE_ENABLED', False)

if environment in ['DEVELOP']:
    EMAIL_AUTORESPONSE_ENABLED = True

if environment not in ['LOCAL', 'UNDEFINED']:
    # govDelivery TMS settings
    EMAIL_BACKEND = 'tms.backend.TMSEmailBackend'
    TMS_AUTH_TOKEN = os.environ.get('TMS_AUTH_TOKEN', '')
    TMS_TARGET_ENDPOINT = TMS_STAGING_ENDPOINT

    if TMS_AUTH_TOKEN and TMS_WEBHOOK_ALLOWED_CIDR_NETS:
        EMAIL_ENABLED = True

    if environment == 'PRODUCTION':
        TMS_TARGET_ENDPOINT = TMS_PRODUCTION_ENDPOINT
        RESTRICT_EMAIL_RECIPIENTS_TO = []

# Private S3 bucket configuration
if environment in ['PRODUCTION', 'STAGE', 'DEVELOP']:
    for service in vcap['s3']:
        if service['instance_name'] == 'sso-creds':
            priv_s3_creds = service['credentials']

    PRIV_S3_BUCKET = priv_s3_creds['bucket']
    PRIV_S3_REGION = priv_s3_creds['region']
    PRIV_S3_ACCESS_KEY_ID = priv_s3_creds['access_key_id']
    PRIV_S3_SECRET_ACCESS_KEY = priv_s3_creds['secret_access_key']
    PRIV_S3_ENDPOINT = priv_s3_creds['endpoint']
    PRIV_S3_ENDPOINT_URL = f'https://{PRIV_S3_ENDPOINT}'
else:
    PRIV_S3_BUCKET = 'crt-private'
    PRIV_S3_REGION = 'region'
    PRIV_S3_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'AWSAKID')
    PRIV_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'AWSSAK')
    PRIV_S3_ENDPOINT_URL = 'http://localhost:4566'

# for AUTH, in prod and stage
if environment in ['PRODUCTION', 'STAGE']:
    for service in vcap['user-provided']:
        if service['instance_name'] == "VCAP_SERVICES":
            # SECURITY WARNING: keep the secret key used in production secret!
            creds = service['credentials']
            AUTH_CLIENT_ID = creds['AUTH_CLIENT_ID']
            AUTH_SERVER = creds['AUTH_SERVER']
            AUTH_USERNAME_CLAIM = creds['AUTH_USERNAME_CLAIM']
            AUTH_GROUP_CLAIM = creds['AUTH_GROUP_CLAIM']

    INSTALLED_APPS.append('django_auth_adfs')
    AUTHENTICATION_BACKENDS = (
        'django_auth_adfs.backend.AdfsAuthCodeBackend',
    )
    MIDDLEWARE.append('django_auth_adfs.middleware.LoginRequiredMiddleware')

    client_sso = boto3.client(
        's3',
        PRIV_S3_REGION,
        aws_access_key_id=PRIV_S3_ACCESS_KEY_ID,
        aws_secret_access_key=PRIV_S3_SECRET_ACCESS_KEY,
    )

    with open('ca_bundle.pem', 'wb') as DATA:
        client_sso.download_file(PRIV_S3_BUCKET, 'sso/ca_bundle.pem', 'ca_bundle.pem')

    # See settings reference https://django-auth-adfs.readthedocs.io/en/latest/settings_ref.html
    AUTH_ADFS = {
        "SERVER": AUTH_SERVER,
        "CLIENT_ID": AUTH_CLIENT_ID,
        "RELYING_PARTY_ID": os.environ.get('AUTH_RELYING_PARTY_ID'),
        "AUDIENCE": os.environ.get('AUTH_AUDIENCE'),
        "CA_BUNDLE": os.path.join(BASE_DIR, 'ca_bundle.pem'),
        "CLAIM_MAPPING": {"first_name": "givenname",
                          "last_name": "surname",
                          "email": "emailaddress"},
        "USERNAME_CLAIM": AUTH_USERNAME_CLAIM,
        "GROUP_CLAIM": AUTH_GROUP_CLAIM,
        'LOGIN_EXEMPT_URLS': [
            '^$',
            '^report',
            '^robots.txt',
            '^privacy-policy',
            '^hate-crime-human-trafficking',
            '^i18n',
            '^email',
        ],
    }

    # Configure django to redirect users to the right URL for login
    LOGIN_URL = "/oauth2/login"
    # The url where the ADFS server calls back to our app
    LOGIN_REDIRECT_URL = "/oauth2/callback"

    ALLOWED_HOSTS = [
        'civilrights.justice.gov',
        'www.civilrights.justice.gov',
        'crt-portal-django-prod.app.cloud.gov',
        'crt-portal-django-stage.app.cloud.gov',
    ]

STATIC_URL = '/static/'

if environment not in ['LOCAL', 'UNDEFINED']:
    for service in vcap['s3']:
        if service['instance_name'] == 'crt-s3':
            # Public AWS S3 bucket for the app
            s3_creds = service["credentials"]

    # Public AWS S3 bucket for the app
    AWS_ACCESS_KEY_ID = s3_creds["access_key_id"]
    AWS_SECRET_ACCESS_KEY = s3_creds["secret_access_key"]
    AWS_STORAGE_BUCKET_NAME = s3_creds["bucket"]
    AWS_S3_REGION_NAME = s3_creds["region"]
    AWS_DEFAULT_REGION = s3_creds["region"]
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3-{AWS_S3_REGION_NAME}.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = 'static'
    AWS_QUERYSTRING_AUTH = False
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'cts_forms.storages.PrivateS3Storage'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_IS_GZIPPED = True

if environment in ['PRODUCTION', 'STAGE', 'DEVELOP']:
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')
    bucket = f"{STATIC_URL}"
    allowed_sources = (
        "'self'",
        bucket,
        'www.civilrights.justice.gov',
        'civilrights.justice.gov',
        'https://touchpoints.app.cloud.gov',
        'https://dap.digitalgov.gov',
        'https://www.google-analytics.com',
        'https://www.googletagmanager.com/',
    )
    # headers required for security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    # If this is set to True, client-side JavaScript will not be able to access the language cookie.
    SESSION_COOKIE_HTTPONLY = True
    # see settings options https://django-csp.readthedocs.io/en/latest/configuration.html#configuration-chapter
    CSP_DEFAULT_SRC = allowed_sources
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSP_SCRIPT_SRC = (
        "'self'",
        bucket,
        'www.civilrights.justice.gov',
        'civilrights.justice.gov',
        'https://dap.digitalgov.gov',
        'https://www.google-analytics.com',
        'https://touchpoints.app.cloud.gov',
        'https://www.googletagmanager.com/',
    )
    CSP_CONNECT_SRC = (
        "'self'",
        bucket,
        'www.civilrights.justice.gov',
        'civilrights.justice.gov',
        'https://dap.digitalgov.gov',
        'https://www.google-analytics.com',
        'https://touchpoints.app.cloud.gov',
        'https://www.googletagmanager.com/',
    )
    CSP_IMG_SRC = allowed_sources
    CSP_MEDIA_SRC = allowed_sources
    CSP_FRAME_SRC = allowed_sources
    CSP_WORKER_SRC = allowed_sources
    CSP_FRAME_ANCESTORS = allowed_sources
    CSP_STYLE_SRC = (
        "'self'",
        bucket,
        'www.civilrights.justice.gov',
        'civilrights.justice.gov',
        "'unsafe-inline'",
        'https://fonts.googleapis.com',
    )
    CSP_FONT_SRC = (
        "'self'",
        bucket,
        'www.civilrights.justice.gov',
        'civilrights.justice.gov',
        "'unsafe-inline'",
        'https://fonts.gstatic.com',
    )
    CSP_INCLUDE_NONCE_IN = ['script-src']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# This is where source assets are collect from by collect static
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )
# Enable for admin storage
# MEDIA_URL = 'media/'
# Where assets are served by web server
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_FILTERS = {
    'css': [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter',
        'compressor.filters.template.TemplateFilter'
    ],
    'js': [
        'compressor.filters.jsmin.JSMinFilter',
    ]
}

COMPRESS_PRECOMPILERS = (
    ('module', 'compressor_toolkit.precompilers.ES6Compiler'),
    ('css', 'compressor_toolkit.precompilers.SCSSCompiler'),
)

# would like to add this before public release
COMPRESS_ENABLED = False

# adding better messaging
CSRF_FAILURE_VIEW = 'cts_forms.views_public.csrf_failure'

# disable logging filters
DEFAULT_LOGGING['handlers']['console']['filters'] = []

LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    "formatters": {"json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"}},
    'handlers': {
        'console': {
            # logging handler that outputs log messages to terminal
            'class': 'logging.StreamHandler',
            "formatter": "json",
            'level': 'INFO',  # message level to be written to console
        },
    },
    'loggers': {
        '': {
            # this sets root level logger to log debug and higher level
            # logs to console. All other loggers inherit settings from
            # root level logger.
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,  # this tells logger to send logging message
                                 # to its parent (will send if set to True)
        },
        'django.db': {
            # django also has database level logging
            'level': 'INFO'
        },
    },
}

AV_SCAN_URL = os.getenv('AV_SCAN_URL')
AV_SCAN_MAX_ATTEMPTS = 10

ENABLE_LOCAL_ATTACHMENT_STORAGE = False
if USE_LOCALSTACK:
    from .localstack_settings import *  # noqa: F401,F403
elif environment == 'LOCAL':
    ENABLE_LOCAL_ATTACHMENT_STORAGE = True

if environment == 'LOCAL':
    from .local_settings import *  # noqa: F401,F403

# Don't activate the debug toolbar in a test environment; it can unexpectedly
# output HTML content that will break test assertions
if TESTING:
    ENABLE_DEBUG_TOOLBAR = False

# Django debug toolbar setup
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += ['debug_toolbar', ]
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware', ] + MIDDLEWARE
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda _: True}
