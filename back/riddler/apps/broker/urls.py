from django.urls import include, path
from rest_framework.routers import DefaultRouter

from riddler.config import settings

from . import views
from .models.platform_config import PlatformConfig, PlatformTypes
from .views.platforms import TelegramBotView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"messages", views.MessageView, basename="messages")
router.register(r"platform_bots", views.PlatformBotView, basename="platform_bots")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("chat/", views.chat, name="chat"),
    path("chat/<str:conversation>/<str:fsm>/", views.room, name="room"),
]
for pb in PlatformConfig.objects.all():
    if pb.platform_type == PlatformTypes.telegram.value:
        urlpatterns.append(
            path(f"webhooks/telegram/{pb.platform_meta['token']}", TelegramBotView.as_view(), name=pb.platform_view_name())
        )
