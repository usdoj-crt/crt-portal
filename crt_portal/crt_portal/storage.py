from django.contrib.staticfiles.storage import ManifestFilesMixin
# note that this import will throw errors if SECRET_KEY is not set
from storages.backends.s3boto3 import S3Boto3Storage


class ManifestS3FilesStorage(ManifestFilesMixin, S3Boto3Storage):
    def read_manifest(self):
        """
        Work around a bug where S3Boto3Storage throws IOError but
        ManifestFilesMixin expects FileNotFound.
        """
        try:
            return super(ManifestS3FilesStorage, self).read_manifest()
        except IOError:
            return None
