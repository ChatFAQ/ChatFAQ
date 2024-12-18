import re

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


def transform_url(url):
    # Extract the bucket name and region
    match = re.search(r'https://([^.]+)\.digitaloceanspaces\.com/([^/]+)', url)
    if match:
        region = match.group(1)
        bucket_name = match.group(2)
        
        # Replace the beginning of the URL
        new_url = re.sub(
            f'https://{region}.digitaloceanspaces.com/{bucket_name}',
            f'https://{bucket_name}.{region}.digitaloceanspaces.com',
            url
        )
        
        return new_url
    else:
        return url  # Return original URL if pattern doesn't match


class PublicMediaS3Storage(S3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaS3Storage(S3Boto3Storage):
    default_acl = "private"
    file_overwrite = False
    custom_domain = False

    def generate_presigned_url(self, path, content_type, expires_in=3600):
        """
        Generate a presigned URL for a PUT request to the given path and content type.
        Expires in 2 hours by default.
        """
        url = self.connection.meta.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket_name, "Key": path, "ContentType": content_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
        print(f"Generated presigned URL: {url}")
        url = transform_url(url)
        print(f"Transformed presigned URL: {url}")
        return url

class PrivateMediaLocalStorage(FileSystemStorage):
    location = settings.MEDIA_ROOT


def select_private_storage():
    return PrivateMediaLocalStorage() if settings.LOCAL_STORAGE else PrivateMediaS3Storage()
