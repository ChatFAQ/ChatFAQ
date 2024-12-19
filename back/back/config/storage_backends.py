import boto3
from botocore.config import Config

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


class PublicMediaS3Storage(S3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaS3Storage(S3Boto3Storage):
    default_acl = "private"  # Set default ACL to 'private' for secure uploads
    file_overwrite = False  # Prevent files with the same name from being overwritten

    def generate_presigned_url_put(
        self,
        path: str,
        content_type: str = "application/octet-stream",
        expires_in: int = 3600,
    ):
        return self.connection.meta.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket_name, "Key": path, "ContentType": content_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
    
    def generate_presigned_url_get(
        self,
        path: str,
        expires_in: int = 3600,
    ):
        return self.connection.meta.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": path,
            },
            ExpiresIn=expires_in,
            HttpMethod="GET",
        )
    
class PrivateMediaLocalStorage(FileSystemStorage):
    location = settings.MEDIA_ROOT


def select_private_storage():
    return (
        PrivateMediaLocalStorage()
        if settings.LOCAL_STORAGE
        else PrivateMediaS3Storage()
    )
