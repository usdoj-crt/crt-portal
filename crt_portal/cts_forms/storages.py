from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PrivateS3Storage(S3Boto3Storage):
    bucket_name = settings.PRIV_S3_BUCKET
    access_key = settings.PRIV_S3_ACCESS_KEY_ID
    secret_key = settings.PRIV_S3_SECRET_ACCESS_KEY
    location = ''
