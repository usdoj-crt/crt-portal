from storages.backends.s3boto3 import S3Boto3Storage


class AttachmentStorage(S3Boto3Storage):
    bucket_name = 'attachments'
    location = ''
