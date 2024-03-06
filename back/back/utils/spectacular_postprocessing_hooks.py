from django.apps import apps
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor, ManyToManyDescriptor
models = apps.get_models()

extras = {
    "AdminUser": "User"
}


def postprocess_schema_foreign_keys(result, generator, **kwargs):
    schemas = result.get('components', {}).get('schemas', {})
    for schema_name, info in schemas.items():
        for model in models:
            if model.__name__ == schema_name or model.__name__ == extras.get(schema_name):
                for prop_name, prop_schema in info.get("properties", {}).items():
                    try:
                        model_class_field = getattr(model, prop_name)
                    except AttributeError:
                        continue
                    if model._meta.get_field(prop_name).get_internal_type() == "FileField":
                        prop_schema['type'] = 'file'
                    if type(model_class_field) is ForwardManyToOneDescriptor:
                        prop_schema['$ref'] = f'#/components/schemas/{model_class_field.field.related_model.__name__}'
                    elif type(model_class_field) is ManyToManyDescriptor:
                        prop_schema['items']['$ref'] = f'#/components/schemas/{model_class_field.field.related_model.__name__}'
                break
    return result
