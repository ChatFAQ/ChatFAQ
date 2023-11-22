from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"people", views.MeViewSet, basename="people")
router.register(r"users", views.UserAPIViewSet, basename="users")
router.register(r"groups", views.GroupAPIViewSet, basename="users")
router.register(r"permissions", views.PermissionAPIViewSet, basename="permissions")
router.register(r"content-types", views.ContentTypeAPIViewSet, basename="content-types")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
