from django.contrib.auth.management.commands.createsuperuser import (
    Command as CreatesuperuserCommand,
)
from django.core import exceptions


class Command(CreatesuperuserCommand):
    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if field.name == "rpc_group":
            if raw_value == "y":
                field.is_active = True
                raw_value = True
            else:
                field.is_active = False
                raw_value = False

        if default and raw_value == "":
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % "; ".join(e.messages))
            val = None

        return val
