from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework.routers import DefaultRouter, SimpleRouter
from knox import views as knox_views

from back.apps.people.views import LoginView

admin.site.site_title = _("ChatFAQ's back-end server")
admin.site.site_header = _("ChatFAQ's back-end server")


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("back/admin/", admin.site.urls),
    path('back/api/login/', LoginView.as_view(), name='knox_login'),
    path('back/api/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('back/api/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path("back/api/", include("back.apps.urls")),
]

if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns = [
        path(
            "back/api/schema/",
            SpectacularAPIView.as_view(),
            name="schema",
        ),
        path(
            "back/api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "back/api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ] + urlpatterns
