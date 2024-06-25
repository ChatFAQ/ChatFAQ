"""
Global configuration of pytest is done in the [pyproject.toml](../pyproject.toml) file.
However, here is a place to put configuration that is specific to the BDD tests.
"""

import os

from .hooks import *  # noqa: F401, F403

# Allow async code to be run in Django tests
# @see: https://github.com/microsoft/playwright-pytest/issues/29
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
