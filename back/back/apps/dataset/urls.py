from django.urls import path

from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("datasets/", views.DatasetAPIView.as_view()),
    path("items/", views.ItemAPIView.as_view()),
    path("utterances/", views.UtteranceAPIView.as_view()),
]
