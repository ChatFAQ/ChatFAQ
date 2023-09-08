import os
from importlib import metadata

from dj_database_url import config as db_config
from model_w.env_manager import EnvManager
from model_w.preset.django import ModelWDjango

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
        return metadata.version("back")
    except metadata.PackageNotFoundError:
        return "0.0.0"


def is_true(s):
    return str(s).lower() in ["yes", "true", "1"]


model_w_django = ModelWDjango(enable_storages=True)

with EnvManager(model_w_django) as env:
    # ---
    # Apps
    # ---

    INSTALLED_APPS += [
        "daphne",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_extensions",
        "simple_history",
        "corsheaders",
        "django_better_admin_arrayfield",
        "rest_framework",
        "rest_framework.authtoken",
        "knox",
        "django_filters",
        "drf_spectacular",
        "drf_spectacular_sidecar",
        "back.apps.people",
        "back.apps.broker",
        "back.apps.fsm",
        "back.apps.language_model",
    ]
    if not os.getenv("REDIS_URL"):
        INSTALLED_APPS += [
            "channels_postgres",
        ]
    MIDDLEWARE += [
        "corsheaders.middleware.CorsMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "simple_history.middleware.HistoryRequestMiddleware",
    ]

    CORS_ALLOW_ALL_ORIGINS = True

    # ---
    # Plumbing
    # ---

    ROOT_URLCONF = "back.config.urls"

    WSGI_APPLICATION = "back.config.wsgi.application"
    ASGI_APPLICATION = "back.config.asgi.application"

    # ---
    # Password validation
    # https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
    # ---

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

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

    REST_FRAMEWORK = {
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "DEFAULT_AUTHENTICATION_CLASSES": ("knox.auth.TokenAuthentication",),
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend"
        ],
    }

    SPECTACULAR_SETTINGS = {
        "TITLE": "ChatFAQ's back-end server",
        "VERSION": get_package_version(),
        "SERVE_INCLUDE_SCHEMA": False,
        "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
        "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
        "REDOC_DIST": "SIDECAR",
    }

    # ---
    # Django Channels
    # ---
    if not os.getenv("REDIS_URL"):
        CHANNEL_LAYERS = {
            "default": {
                "BACKEND": "back.utils.custom_channel_layer.CustomPostgresChannelLayer",
                "CONFIG": {
                    **db_config(conn_max_age=None),
                    "config": {
                        "maxsize": 0,  # unlimited pool size (but it recycles used connections of course)
                    },
                },
            },
        }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
            "CONFIG": {
                "hosts": [model_w_django._redis_url(env)],
                "prefix": model_w_django._redis_prefix(env, "channels"),
                "capacity": 1500,  # default 100
                "expiry": 5,  # default 60
            },
        },
    }
    # ---
    # Logging
    # ---
    """
    SIMPLE_LOG = True
    LOGGING_CONFIG = "logging.config.dictConfig"
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"()": "back.utils.logging_formatters.DjangoJsonFormatter"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG" if is_true(preset._debug(env)) else "INFO",
        },
    }
    """

    # ---
    # Telegram
    # ---

    TG_TOKEN = os.getenv("TG_TOKEN")
    # SPECTACULAR_SETTINGS = {
    #     "POSTPROCESSING_HOOKS": [
    #         "back.apps.broker.serializers.messages.custom_postprocessing_hook"
    #     ]
    # }

    REST_KNOX = {
        "TOKEN_TTL": None,
    }
    # Celery
    # CELERY_BROKER_URL = f"sqla+{os.getenv('DATABASE_URL')}"
    # from kombu.common import Broadcast
    # CELERY_QUEUES = (Broadcast('broadcast_tasks'),)
    # CELERY_ROUTES = {
    #     'back.apps.language_model.tasks.recache_models': {
    #         'queue': 'broadcast_tasks',
    #         'exchange': 'broadcast_tasks'
    #     },
    # }
