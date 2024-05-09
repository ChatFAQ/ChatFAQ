import sys
from logging import getLogger
from ray.util.state import api as ray_api
from datetime import datetime



logger = getLogger(__name__)


def is_ray_worker():
    """
    Check if the current process is a Ray worker.
    """
    return any("ray" in s for s in sys.argv)
