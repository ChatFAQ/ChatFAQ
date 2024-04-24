from django.utils.translation import gettext_lazy as _
from django.db import models


class IndexStatusChoices(models.TextChoices):
    NO_INDEX = "no_index", _("No Index")
    OUTDATED = "outdated", _("Outdated")
    UP_TO_DATE = "up_to_date", _("Up to Date")


class DeviceChoices(models.TextChoices):
    CPU = "cpu", _("CPU")
    CUDA = "cuda", _("GPU")


class RetrieverTypeChoices(models.TextChoices):
    COLBERT = "colbert", _("ColBERT Search")
    E5 = "e5", _("Standard Semantic Search")


class LLMChoices(models.TextChoices):
    VLLM = "vllm", _("VLLM Client")
    OPENAI = "openai", _("OpenAI Model")
    CLAUDE = "claude", _("Claude Model")
    MISTRAL = "mistral", _("Mistral Model")
    TOGETHER = "together", _("Together Model")
    # Deprecated for now
    # LOCAL_CPU = 'local_cpu', _('Local CPU Model')
    # LOCAL_GPU = 'local_gpu', _('Local GPU Model')

class LanguageChoices(models.TextChoices):
    EN = "en", _("English")
    ES = "es", _("Spanish")
    FR = "fr", _("French")

class StrategyChoices(models.TextChoices):
    AUTO = "auto", _("Auto")
    FAST = "fast", _("Fast")
    OCR_ONLY = "ocr_only", _("OCR Only")
    HI_RES = "hi_res", _("Hi Res")

class SplittersChoices(models.TextChoices):
    SENTENCES = "sentences", _("Sentences")
    WORDS = "words", _("Words")
    TOKENS = "tokens", _("Tokens")
    SMART = "smart", _("Smart")