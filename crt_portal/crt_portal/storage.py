from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage

class CachedS3Boto3Storage(S3Boto3Storage):
    """
    Save compressed files to local storage before uploading to S3.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3Boto3Storage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class("compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        self.local_storage._save(name, content)
        super(CachedS3Boto3Storage, self).save(name, self.local_storage._open(name))
        return name
