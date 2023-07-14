from django.forms import ModelForm

from .models import PromptStructure


class PromptStructureForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PromptStructureForm, self).__init__(*args, **kwargs)
        self.fields['user_tag'].strip = False
        self.fields['assistant_tag'].strip = False
        self.fields['system_tag'].strip = False

    class Meta:
        model = PromptStructure
        fields = "__all__"
