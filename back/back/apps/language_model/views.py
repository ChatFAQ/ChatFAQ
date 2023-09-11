import csv

from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Dataset, Item, Model, Utterance
from .serializers import (
    DatasetSerializer,
    ItemSerializer,
    ModelSerializer,
    UtteranceSerializer, DatasetFromUrlSerializer
)


class DatasetAPIViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    @action(detail=True)
    def download_csv(self, request, *args, **kwargs):
        """
        A view to download all the dataset's items as a csv file:
        """
        ds = Dataset.objects.get(pk=kwargs["pk"])
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename={}'.format(
            ds.name + ".csv"
        )
        response.write(ds.to_csv())
        return response


class ItemAPIViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filterset_fields = ["dataset__id"]


class UtteranceAPIViewSet(viewsets.ModelViewSet):
    queryset = Utterance.objects.all()
    serializer_class = UtteranceSerializer
    filterset_fields = ["item__id"]


class ModelAPIViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
