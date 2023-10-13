from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from back.apps.language_model.models.data import KnowledgeBase, KnowledgeItem
from back.apps.language_model.models.rag_pipeline import AutoGeneratedTitle
from back.apps.language_model.serializers.data import KnowledgeBaseSerializer, KnowledgeItemSerializer, \
    AutoGeneratedTitleSerializer


class KnowledgeBaseAPIViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer

    def get_queryset(self):
        if self.kwargs.get("pk"):
            kb = KnowledgeBase.objects.filter(name=self.kwargs["pk"]).first()
            if kb:
                self.kwargs["pk"] = str(kb.pk)
        return super().get_queryset()

    @action(detail=True)
    def download_csv(self, request, *args, **kwargs):
        """
        A view to download all the knowledge base's items as a csv file:
        """
        kb = KnowledgeBase.objects.filter(name=kwargs["pk"]).first()
        if not kb:
            kb = KnowledgeBase.objects.get(pk=kwargs["pk"])
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename={}'.format(
            kb.name + ".csv"
        )
        response.write(kb.to_csv())
        return response


class KnowledgeItemAPIViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer
    filterset_fields = ["knowledge_base__id", "knowledge_base__name"]

    def create(self, request, *args, **kwargs):
        """
        A view to create a new knowledge item:
        """
        return super().create(request, *args, **kwargs)


class AutoGeneratedTitleAPIViewSet(viewsets.ModelViewSet):
    queryset = AutoGeneratedTitle.objects.all()
    serializer_class = AutoGeneratedTitleSerializer
    filterset_fields = ["knowledge_item__id", "knowledge_item__name"]
