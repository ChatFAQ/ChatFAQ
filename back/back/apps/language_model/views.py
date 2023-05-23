import csv

from .models import Dataset, Item, Utterance, Model
from .serializers import DatasetSerializer, ItemSerializer, UtteranceSerializer, ModelSerializer
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse


class DatasetAPIViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        ds = Dataset.objects.get(pk=serializer.data["id"])
        decoded_file = ds.original_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            item = Item(
                dataset=ds,
                intent=row['intent'],
                answer=row['answer'],
                url=row['url'],
                context=row.get('context'),
                role=row.get('role'),
            )
            item.save()

    @action(detail=True)
    def download_csv(self, request, *args, **kwargs):
        """
        A view to download all the dataset's items as a csv file:
        """
        ds = Dataset.objects.get(pk=kwargs['pk'])
        items = Item.objects.filter(dataset=ds)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(ds.name + '.csv')
        writer = csv.writer(response)
        writer.writerow(['intent', 'answer', 'url', 'context', 'role'])
        for item in items:
            writer.writerow([item.intent, item.answer, item.url, item.context, item.role])
        return response


class ItemAPIViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filterset_fields = ['dataset__id']


class UtteranceAPIViewSet(viewsets.ModelViewSet):
    queryset = Utterance.objects.all()
    serializer_class = UtteranceSerializer
    filterset_fields = ['item__id']


class ModelAPIViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
