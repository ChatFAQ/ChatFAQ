import os

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


class PublicMediaS3Storage(S3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaS3Storage(S3Boto3Storage):
    default_acl = "private"
    file_overwrite = False
    custom_domain = False

    def generate_presigned_url(self, path, content_type, expires_in=7200):
        """
        Generate a presigned URL for a PUT request to the given path and content type.
        Expires in 2 hours by default.
        """
        return self.connection.meta.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket_name, "Key": path, "ContentType": content_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )

class PrivateMediaLocalStorage(FileSystemStorage):
    location = settings.MEDIA_ROOT


def select_private_storage():
    return PrivateMediaLocalStorage() if settings.LOCAL_STORAGE else PrivateMediaS3Storage()
