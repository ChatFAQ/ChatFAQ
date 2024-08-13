from django.forms import ModelForm, ChoiceField
from django.forms.utils import ErrorList

from back.apps.broker.models import RemoteSDKParsers
from back.apps.language_model.models import DataSource
from back.apps.language_model.serializers.data import DataSourceSerializer


def get_parser_choices():
    choices = RemoteSDKParsers.objects.all().values_list("parser_name", flat=True).distinct()
    return [(None, "")] + [(choice, choice) for choice in choices]


class DataSourceForm(ModelForm):
    parser = ChoiceField(choices=get_parser_choices, required=False)

    class Meta:
        model = DataSource
        fields = "__all__"

    def is_valid(self):
        # Call super's is_valid to populate cleaned_data and do basic field validation
        valid = super(DataSourceForm, self).is_valid()
        if not valid:
            return False
        serializer = DataSourceSerializer(data=self.cleaned_data)
        if not serializer.is_valid():
            for field in serializer.errors:
                _field = field if field != "non_field_errors" else "original_csv"
                errors = self._errors.setdefault(_field, ErrorList())
                for e in serializer.errors[field]:
                    errors.append(e)
            return False
        return True
