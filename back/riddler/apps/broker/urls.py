from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"messages", views.MessageView, basename="messages")
router.register(r"platform_bots", views.PlatformConfigView, basename="platform_bots")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("chat/", views.chat, name="chat"),
    path("chat/<str:conversation>/<str:pc_id>/", views.room, name="room"),
]
