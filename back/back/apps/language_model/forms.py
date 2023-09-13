from django.forms import ModelForm

from back.apps.language_model.models.rag_pipeline import PromptConfig


class PromptConfigForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PromptConfigForm, self).__init__(*args, **kwargs)
        self.fields['user_tag'].strip = False
        self.fields['assistant_tag'].strip = False
        self.fields['system_tag'].strip = False

    class Meta:
        model = PromptConfig
        fields = "__all__"
