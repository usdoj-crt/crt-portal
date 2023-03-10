"""Reminder not to put secrets in this file, it is in source control """
import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',  # set in docker-compose.yml
        'PORT': 5432  # default postgres port
    }
}

SECRET_KEY = os.getenv('SECRET_KEY')
# Convert string to boolean
VOTING_MODE = (os.getenv('VOTING_MODE', 'False') == 'True')
# This setting will only be used in local development
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '10.0.2.2', '0.0.0.0', 'web']  # nosec
# This allows jupyter to make requests to the Portal for auth.
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8001',  # External-to-docker Jupyterhub IP
    'http://jupyterhub',  # Internal-to-docker Jupyterhub Hostname
]
DEBUG = True
ENABLE_DEBUG_TOOLBAR = True

# Local email development
EMAIL_HOST = 'mailhog'
EMAIL_PORT = 1025
EMAIL_ENABLED = True
RESTRICT_EMAIL_RECIPIENTS_TO = []
EMAIL_AUTORESPONSE_ENABLED = True
