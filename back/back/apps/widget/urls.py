from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"widgets", views.WidgetAPIViewSet, basename="widgets")
router.register(r"themes", views.ThemeAPIViewSet, basename="themes")

urlpatterns = [
    path(r'theme-defaults/', views.ThemeDefaultsAPIViewSet.as_view(), name='theme_defaults'),
    path("", include(router.urls)),
]
