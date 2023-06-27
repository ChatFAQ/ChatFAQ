from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

# The API URLs are now determined automatically by the router.
router = DefaultRouter()
router.register(r"datasets", views.DatasetAPIViewSet, basename="dataset")
router.register(r"models", views.ModelAPIViewSet, basename="model")
router.register(r"items", views.ItemAPIViewSet, basename="item")
router.register(r"utterances", views.UtteranceAPIViewSet, basename="utterance")

urlpatterns = router.urls
