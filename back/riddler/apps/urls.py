from django.urls import include, re_path

urlpatterns = [
    re_path(r"broker/", include("riddler.apps.broker.urls")),
    re_path(r"fsm/", include("riddler.apps.fsm.urls")),
    re_path(r"people/", include("riddler.apps.people.urls")),
]
