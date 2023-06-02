import os
from importlib import metadata

from model_w.env_manager import EnvManager
from model_w.preset.django import ModelWDjango

REST_FRAMEWORK = {}
MIDDLEWARE = []
INSTALLED_APPS = []
LOGGING = {}


def get_package_version() -> str:
    """
    Trying to get the current package version using the metadata module. This
    assumes that the version is indeed set in pyproject.toml and that the
    package was cleanly installed.
    """

    try:
        return metadata.version("chatfaq_retrieval_server")
    except metadata.PackageNotFoundError:
        return "0.0.0"


preset = ModelWDjango()

dotenv_path = None
if os.getenv("DOCKER_CONTAINER"):
    dotenv_path = False

with EnvManager(preset, dotenv_path=dotenv_path) as env:
    # ---
    # Apps
    # ---

    INSTALLED_APPS = [
        "drf_spectacular",
        "drf_spectacular_sidecar",
        "django.contrib.staticfiles",
        "chatfaq_retrieval_server.apps.realtime",
        "chatfaq_retrieval_server.apps.people",
    ]

    # ---
    # Plumbing
    # ---

    ROOT_URLCONF = "chatfaq_retrieval_server.config.urls"

    WSGI_APPLICATION = "chatfaq_retrieval_server.config.wsgi.application"
    ASGI_APPLICATION = "chatfaq_retrieval_server.config.asgi.application"

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
        "TITLE": "ChatFAQ Retrieval Server",
        "VERSION": get_package_version(),
        "SERVE_INCLUDE_SCHEMA": False,
        "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
        "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
        "REDOC_DIST": "SIDECAR",
    }

    CACHED_MODELS = {

    }
