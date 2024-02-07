from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets


@extend_schema_view(
    list=extend_schema(parameters=[OpenApiParameter("fields", type=str, many=True)])
)
class DynamicFieldsView(viewsets.ModelViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()

        fields = None
        if self.request.method == "GET":
            query_fields = self.request.query_params.get("fields", None)

            if query_fields:
                fields = tuple(query_fields.split(","))

        kwargs["context"] = self.get_serializer_context()
        kwargs["fields"] = fields

        return serializer_class(*args, **kwargs)
