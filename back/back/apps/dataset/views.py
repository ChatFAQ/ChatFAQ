import csv

from .models import Dataset, Item, Utterance
from .serializers import DatasetSerializer, ItemSerializer, UtteranceSerializer
from rest_framework import generics


class DatasetAPIView(
    generics.ListCreateAPIView,
    generics.DestroyAPIView
):
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


class ItemAPIView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filterset_fields = ['dataset__id']


class UtteranceAPIView(generics.ListCreateAPIView):
    queryset = Utterance.objects.all()
    serializer_class = UtteranceSerializer
    filterset_fields = ['item__id']
