from django.urls import path, re_path

from .views import global_status, global_status_json

urlpatterns = [
    path("global-status/", global_status, name="global-status"),
    path("global-status.json", global_status_json, name="global-status-json"),
]
