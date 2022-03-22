# Django storages configurations to use localstack container

import os

# Ignored by localstack but required by django-storages, any truthy string should work
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# port defined in docker-compose.yml, localhost because django-storages uses this to build
# staticfile URIs
AWS_S3_ENDPOINT_URL = 'http://localhost:4566'

# Proxy calls to S3 -- like collectstatic -- to the docker conainter
AWS_S3_PROXIES = {'http': 'localstack:4566'}

AWS_STORAGE_BUCKET_NAME = "crt-portal"
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_LOCATION = 'static'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'cts_forms.storages.PrivateS3Storage'
DEFAULT_FILE_STORAGE = 'cts_forms.storages.ManifestS3Storage'
AWS_DEFAULT_ACL = 'public-read'
AWS_IS_GZIPPED = True
