"""Reminder not to put secrets in this file, it is in source control """
import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',  # set in docker-compose.yml
        'PORT': 5432  # default postgres port
    }
}

SECRET_KEY = os.getenv('SECRET_KEY')
# This setting will only be used in local development
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '10.0.2.2', '0.0.0.0']  # nosec
DEBUG = True
