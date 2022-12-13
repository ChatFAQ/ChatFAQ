from importlib import metadata

from model_w.env_manager import EnvManager
from model_w.preset.django import ModelWDjango

REST_FRAMEWORK = {}


def get_package_version() -> str:
    """
    Trying to get the current package version using the metadata module. This
    assumes that the version is indeed set in pyproject.toml and that the
    package was cleanly installed.
    """

    try:
        return metadata.version("riddler")
    except metadata.PackageNotFoundError:
        return "0.0.0"


with EnvManager(ModelWDjango()) as env:
    # ---
    # Apps
    # ---

    INSTALLED_APPS = [
        "drf_spectacular",
        "drf_spectacular_sidecar",
        "riddler.core",
        "riddler.people",
    ]

    # ---
    # Plumbing
    # ---

    ROOT_URLCONF = "riddler.django.urls"

    WSGI_APPLICATION = "riddler.django.wsgi.application"
    ASGI_APPLICATION = "riddler.django.asgi.application"

    # ---
    # Auth
    # ---

    AUTH_USER_MODEL = "people.User"

    # ---
    # i18n
    # ---

    LANGUAGES = [
        ("en", "English"),
    ]

    # ---
    # OpenAPI Schema
    # ---

    REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

    SPECTACULAR_SETTINGS = {
        "TITLE": "Riddler",
        "VERSION": get_package_version(),
        "SERVE_INCLUDE_SCHEMA": False,
        "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
        "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
        "REDOC_DIST": "SIDECAR",
    }

