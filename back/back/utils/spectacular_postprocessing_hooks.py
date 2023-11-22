from django.apps import apps
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
models = apps.get_models()


def postprocess_schema_foreign_keys(result, generator, **kwargs):
    schemas = result.get('components', {}).get('schemas', {})
    for schema_name, info in schemas.items():
        for model in models:
            if model.__name__ == schema_name:
                for prop_name, prop_schema in info.get("properties", {}).items():
                    try:
                        model_class_field = getattr(model, prop_name)
                    except AttributeError:
                        continue
                    if type(model_class_field) is ForwardManyToOneDescriptor:
                        prop_schema['$ref'] = f'#/components/schemas/{model_class_field.field.related_model.__name__}'
                break
    return result
