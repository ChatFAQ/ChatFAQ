from django.urls import include, re_path

urlpatterns = [
    re_path(r"broker/", include("api.broker.urls")),
    re_path(r"fsm/", include("api.fsm.urls")),
]
