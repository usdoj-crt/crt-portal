"""Reminder not to put secrets in this file, it is in source control """
import os
import random
import string

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db', # set in docker-compose.yml
        'PORT': 5432 # default postgres port
    }
}

def randomStringDigits(stringLength=18):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

SECRET_KEY = os.getenv('SECRET_KEY', randomStringDigits(8))
ALLOWED_HOSTS = ['localhost', '0.0.0.0']
DEBUG = True
