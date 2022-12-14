from datetime import datetime

from rest_framework import serializers

from riddler.common.validators import NDigits


class Color:
    """
    A color represented in the RGB colorspace.
    """

    def __init__(self, red, green, blue):
        assert red >= 0 and green >= 0 and blue >= 0
        assert red < 256 and green < 256 and blue < 256
        self.red, self.green, self.blue = red, green, blue


class JSTimestampField(serializers.Field):
    """
    A datetime represented in a 13 digit number.
    """

    def to_representation(self, value):
        return int(value.timestamp() * 1000)

    def to_internal_value(self, value):
        NDigits(13)(value)
        return datetime.fromtimestamp(value / 1000)
