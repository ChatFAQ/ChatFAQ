from django.urls import include, re_path

urlpatterns = [
    re_path(r"broker/", include("back.apps.broker.urls")),
    re_path(r"fsm/", include("back.apps.fsm.urls")),
    re_path(r"people/", include("back.apps.people.urls")),
    re_path(r"language-model/", include("back.apps.language_model.urls")),
]
