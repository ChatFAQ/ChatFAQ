from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"messages", views.MessageView, basename="messages")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    path("conversation/<int:pk>/", views.ConversationView.as_view()),
    path("conversations/<str:pk>/", views.ConversationsInfoView.as_view()),
    path("conversations", views.ConversationsInfoView.as_view()),
    path("conversations-download", views.ConversationsDownload.as_view()),
    path('user-feedbacks/<int:pk>/', views.UserFeedbackAPIView.as_view()),
    path('user-feedbacks/', views.UserFeedbackAPIView.as_view()),
    path('admin-reviews/<int:pk>/', views.AdminReviewAPIView.as_view()),
    path('admin-reviews/', views.AdminReviewAPIView.as_view()),
    path('senders/', views.SenderAPIView.as_view()),
]
