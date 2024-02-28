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


class PrivateMediaLocalStorage(FileSystemStorage):
    location = settings.MEDIA_ROOT


def select_private_storage():
    return PrivateMediaLocalStorage() if settings.LOCAL_STORAGE else PrivateMediaS3Storage()
