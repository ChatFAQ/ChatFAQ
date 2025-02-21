from base64 import b64decode, b64encode
from logging import getLogger

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from ._core import NissaString, get_light_bringer

logger = getLogger(__name__)


class NissaStringField(models.BinaryField):
    """
    Custom model field to store NissaString instances in the database as bytes.
    The point is that apart from when we collect the data, the value is always
    encrypted and cannot be decrypted without the private key which is in
    another part of the code. The value can even be generated from the frontend
    without knowing the private key. Helpful to avoid leaking secrets by
    accident through stack traces or stuff like that.
    """

    description = _("An encrypted string stored securely using NissaString.")

    def __init__(self, *args, **kwargs):
        kwargs = {
            **kwargs,
            "editable": kwargs.get("editable", True),
        }

        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        Converting the bytes from database to NissaString
        """
        if value is None:
            return value

        ns = NissaString.from_bytes(force_bytes(value))
        return ns
    
    def to_python(self, value):
        """
        Making sure the value is always a NissaString
        """
        if value is None or isinstance(value, NissaString):
            return value

        if isinstance(value, str):
            if not settings.AZOR_PRIVATE_KEY:
                logger.warning("AZOR_PRIVATE_KEY is not set, returning None.")
                return None
            lb = get_light_bringer()
            return lb.securize(value)

        raise TypeError("Invalid type for NissaStringField")

    def get_prep_value(self, value):
        """
        Converting the NissaString to bytes before storing it in the database
        """
        if value is None:
            return None

        if isinstance(value, str):
            if not settings.AZOR_PRIVATE_KEY:
                logger.warning("AZOR_PRIVATE_KEY is not set, returning None.")
                return None
            lb = get_light_bringer()
            return lb.securize(value).to_bytes()

        if isinstance(value, NissaString):
            return value.to_bytes()

        raise TypeError("Invalid type for NissaStringField")

    def formfield(self, **kwargs):
        """
        Returns a forms.CharField for this field when encryption is configured,
        otherwise returns a disabled field with a warning message.
        """
        if not settings.AZOR_PRIVATE_KEY:
            kwargs['widget'] = forms.TextInput(attrs={'disabled': 'disabled'})
            kwargs['help_text'] = _("API key storage is not available - encryption is not configured")
        return super().formfield(**kwargs)

    def value_from_object(self, obj):
        """
        Returns the bytes representation of the NissaString.
        """
        value = super().value_from_object(obj)
        if value is None:
            return None
        return value.to_bytes()


