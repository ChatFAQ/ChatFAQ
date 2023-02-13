import json
import logging
from datetime import datetime

from django.conf import settings
from pythonjsonlogger.jsonlogger import JsonFormatter

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"


class DjangoJsonFormatter(JsonFormatter):
    WHITE = "\u001b[37m"
    RESET = "\u001b[0m"
    level_to_colors = {
        "DEBUG": "\033[35m",
        "INFO": "\033[34m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\u001b[41;1m",
    }

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime(TIMESTAMP_FORMAT)
        res = super().format(record)
        color = self.level_to_colors.get(record.levelname, self.WHITE)

        if settings.DEBUG and settings.SIMPLE_LOG:
            return f"{timestamp} {color}{json.loads(res)['message']}{self.RESET}"
        return (
            color
            + json.dumps(
                {
                    **json.loads(res),
                    "timestamp": timestamp,
                    "level": record.levelname,
                    "filename": record.filename,
                    "lineno": record.lineno,
                    "pathname": f".{record.pathname.replace(str(settings.BASE_DIR), '')}",
                },
                indent=4,
            )
            + self.RESET
        )
