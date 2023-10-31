from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from back.apps.language_model.models.data import KnowledgeBase, KnowledgeItem, AutoGeneratedTitle, Intent
from back.apps.language_model.serializers.data import KnowledgeBaseSerializer, KnowledgeItemSerializer, \
    AutoGeneratedTitleSerializer, IntentSerializer

from back.apps.language_model.tasks import generate_suggested_intents_task, generate_intents_task, generate_titles


class KnowledgeBaseAPIViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseSerializer

    def get_queryset(self):
        if self.kwargs.get("pk"):
            kb = KnowledgeBase.objects.filter(name=self.kwargs["pk"]).first()
            if kb:
                self.kwargs["pk"] = str(kb.pk)
        return super().get_queryset()

    @action(detail=True, url_name="download-csv", url_path="download-csv")
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

    @action(detail=True, url_name="generate", url_path="generate", methods=["POST"])
    def generate_titles(self, request, *args, **kwargs):
        """
        A view to generate titles for a Knowledge Base:
        """
        kb = KnowledgeBase.objects.filter(name=kwargs["pk"]).first()
        if not kb:
            return HttpResponse("Knowledge Base not found", status=404)
        n_titles = request.data['n_titles'] if 'n_titles' in request.data else 10
        generate_titles.delay(kb.id, n_titles)
        return JsonResponse({"message": "Task started"})
    

class IntentAPIViewSet(viewsets.ModelViewSet):
    queryset = Intent.objects.all()
    serializer_class = IntentSerializer

    @action(detail=True, url_name="suggest-intents", url_path="suggest-intents", methods=["POST"])
    def suggest_intents(self, request, *args, **kwargs):
        """
        A view to get suggested intents for a Knowledge Base:
        """
        kb = KnowledgeBase.objects.filter(name=kwargs["pk"]).first()
        if not kb:
            return HttpResponse("Knowledge Base not found", status=404)
        # if no AutoGeneratedTitle return error
        if not AutoGeneratedTitle.objects.filter(knowledge_item__knowledge_base=kb).exists():
            return HttpResponse("No auto generated titles found, create them first", status=404)
        
        generate_suggested_intents_task.delay(kb.id)
        return JsonResponse({"message": "Task started"})
    
    @action(detail=True, url_name="generate-intents", url_path="generate-intents", methods=["POST"])
    def generate_intents(self, request, *args, **kwargs):
        """
        A view to generate intents from a Knowledge Base:
        """
        kb = KnowledgeBase.objects.filter(name=kwargs["pk"]).first()
        if not kb:
            return HttpResponse("Knowledge Base not found", status=404)
        # if no AutoGeneratedTitle return error
        if not AutoGeneratedTitle.objects.filter(knowledge_item__knowledge_base=kb).exists():
            return HttpResponse("No auto generated titles found, create them first", status=404)
        
        generate_intents_task.delay(kb.id)
        return JsonResponse({"message": "Task started"})
