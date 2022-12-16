from django.urls import include, path
from rest_framework.routers import DefaultRouter

from riddler.config import settings

from . import views
from .views.platforms import TelegramBotView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"messages", views.MessageView, basename="messages")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("chat/", views.chat, name="chat"),
    path("chat/<str:conversation>/<str:fsm>/", views.room, name="room"),
]

if settings.TG_TOKEN:
    urlpatterns.append(
        path("webhooks/telegram", TelegramBotView.as_view(), name="webhooks_telegram")
    )
