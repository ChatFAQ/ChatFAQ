"""
This file runs all the .feature files found inside ./features/

All tests found in ./features/ are marked as follows:
 - given DB access
 - given a "bdd" tag allowing specific targetting with: `pytest -m bdd`

"""

import pytest
import pytest_bdd

from .fixtures import *  # noqa: F401, F403
from .step_definitions import *  # noqa: F401, F403

# Uses the global pytestmark variable to add the bdd marker and DB access to all tests in this file.
# This means these tests can be specifically targetted with `pytest -m bdd`.
pytestmark = [
    pytest.mark.django_db(transaction=True, serialized_rollback=True),
    pytest.mark.bdd,
]

pytest_bdd.scenarios(
    "./features/",
)
