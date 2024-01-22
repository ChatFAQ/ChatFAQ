from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"messages", views.MessageView, basename="messages")
router.register(
    r"conversations", views.ConversationAPIViewSet, basename="conversations"
)
router.register(
    r"user-feedback", views.UserFeedbackAPIViewSet, basename="user-feedback"
)
router.register(
    r"admin-review", views.AdminReviewAPIViewSet, basename="user-feedback"
)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("senders/", views.SenderAPIView.as_view()),
]
