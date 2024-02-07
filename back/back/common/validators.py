from datetime import datetime

from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr


class AtLeastNOf:
    """
    At least N of the provided fields should have a value

    Should be applied to the serializer class, not to an individual field.
    """

    def __init__(self, fields, number=1):
        self.number = number
        self.fields = fields

    def __call__(self, attrs):
        present = 0
        for key, val in attrs.items():
            if key in self.fields and val is not None:
                present += 1
        if present < self.number:
            raise ValidationError(
                f"At least {self.number} of this fields: {', '.join(self.fields)}, should be present"
            )

    def __repr__(self):
        return f"<{self.__class__.__name__} (N={self.number} fields={smart_repr(self.fields)})>"


class PresentTogether:
    """
    The order of the provided fields matter: from left to right if the field has
    a value then the next one should also have one.

    Should be applied to the serializer class, not to an individual field.
    """

    def __init__(self, fields):
        if not fields:
            raise Exception(
                "You should provide a list of fields with at least one item"
            )
        self.fields = fields

    def _check(self, f, attrs):
        if type(f) == dict:
            expected_v = list(f.values())[0]
            real_v = attrs.get(list(f.keys())[0])
            if expected_v != real_v:
                return (
                    False,
                    f"Field: {f} should have value: {expected_v} instead of: {real_v}",
                )
        else:
            if attrs.get(f) is None:
                return False, f"Field: {f} should be present"
        return True, None

    def __call__(self, attrs):
        _f = self.fields[0]
        if self._check(_f, attrs)[0]:
            for f in self.fields:
                match, error = self._check(f, attrs)
                if not match:
                    raise ValidationError(error)

    def __repr__(self):
        return f"<{self.__class__.__name__} (Always present together: {smart_repr(self.fields)})>"


def valid_timestamp(value):
    """
    Expects a 13 digits number that represents a valid date time

    Should be applied to an individual serializer  field.
    """
    if len(str(value)) != 13:
        raise ValidationError("The timestamp should be a valid 13 digits number")
    dt_object = datetime.fromtimestamp(value / 1000)


class NDigits:
    """
    Expects a 13 digits number that represents a valid date time

    Should be applied to an individual serializer field.
    """

    def __init__(self, n):
        if not n:
            raise Exception("N should be more than 0")
        self.n = n

    def __call__(self, value):
        if len(str(value)) != self.n:
            raise ValidationError(f"Number should have {self.n} digits")

    def __repr__(self):
        return f"<{self.__class__.__name__} (N={self.n})>"
