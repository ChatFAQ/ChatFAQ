from django.urls import include, re_path

urlpatterns = [
    re_path(r"retriever/", include("chatfaq_retrieval_server.apps.retriever.urls")),
]
