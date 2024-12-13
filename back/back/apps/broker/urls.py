from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import FileUploadView

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
    r"admin-review", views.AdminReviewAPIViewSet, basename="admin-review"
)
router.register(
    r"sdks", views.ConsumerRoundRobinQueueViewSet, basename="sdks"
)


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("senders/", views.SenderAPIView.as_view()),
    path("stats/", views.Stats.as_view()),
    path('file-upload/', FileUploadView.as_view(), name='file-upload'),
]
