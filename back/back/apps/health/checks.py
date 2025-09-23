from collections.abc import Mapping, Sequence

from asgiref.sync import async_to_sync
from django.conf import settings
from health_check.cache.backends import CacheBackend
from health_check.contrib.psutil.backends import MemoryUsage
from health_check.db.backends import (
    DatabaseBackend,
    ServiceUnavailable,
    BaseHealthCheckBackend,
)

from .base import DjangoHealthCheckWrapper, HealthCheck, Outcome, Status
from .models import Event


def disp_window(window: Mapping[str, int]) -> str:
    """
    Returns a friendly text for a time window (aka the kwargs of a timedelta)

    Parameters
    ----------
    window
        Window to be displayed
    """

    items = []

    for key, value in window.items():
        if value == 0:
            continue

        if value == 1:
            key = key.rstrip("s")

        items.append(f"{value} {key}")

    return " ".join(items)


def disp_stats(stats: Mapping[str, int]) -> str:
    """
    All the checks relying on the logs use the same pattern of checking how
    many success/failures happened. This is an utility to transform these
    stats into a readable text.

    Parameters
    ----------
    stats
        A dictionary with "success", "failure" and "total" as keys
    """

    success_str, failure_str, total_str = "", "", ""

    if success := stats["success"]:
        plural = "es" if success != 1 else ""
        success_str = f"{success} success{plural}"

    if failure := stats["failure"]:
        plural = "s" if failure != 1 else ""
        failure_str = f"{failure} failure{plural}"

    if total := stats["total"]:
        total_str = f"out of {total}"
    else:
        total_str = "no events"

    part_1 = ", ".join([x for x in [success_str, failure_str] if x])

    return " ".join([x for x in [part_1, total_str] if x]).capitalize()


class Database(DjangoHealthCheckWrapper):
    """
    Checks that the default database can be reached, read and write
    """

    base_class = DatabaseBackend

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; Database cannot be reached

This checks verifies if the database is reachable by inserting and deleting a
row in a test table.

## Possible causes

- There could be a network issue that prevents to access the database
- The data could be inconsistent or the disk full
- The database server could be overloaded

## Possible solutions

- Check the network connectivity
- Check the disk space
- Check the database server logs
- Check the database server status
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["database"]

    def get_name(self) -> str:
        return "Database"


class RamUsage(DjangoHealthCheckWrapper):
    """
    Checks that we don't use too much RAM
    """

    base_class = MemoryUsage

    def get_name(self) -> str:
        return "RAM Usage"

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; RAM usage is too high

The memory usage in the container running the application is too high.

## Possible causes

- There is a memory leak in the application
- The application just needs more RAM

## Possible solutions

- Short term, restart the container
- Long term, identify if this issue comes from a leak (in which case you can
  fix the leak) or if the application just needs more RAM (in which case you
  can increase the RAM allocated to the container)
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["api"]


# :: IF api__redis


class Cache(DjangoHealthCheckWrapper):
    """
    Validates cache accessibility. Since the queue is also the cache, it will
    validate the queue as well (somehow).
    """

    base_class = CacheBackend

    def get_name(self) -> str:
        return "Cache"

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; Redis cache cannot be reached

This checks verifies if the cache is reachable by inserting and deleting an
entry in the cache.

## Possible causes

- There could be a network issue that prevents to access the cache
- The cache could be overloaded

## Possible solutions

- Check the network connectivity
- Check the cache server logs
- Check the cache server status
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["redis"]


# :: ENDIF


class ProcrastinateBuiltInHealthCheck(BaseHealthCheckBackend):
    """
    Health check for Procrastinate task processor.

    Uses the built-in healthchecks to check if the Procrastinate app is
    working.
    """

    def __init__(self):
        """
        Get the Procrastinate app from the settings.
        If not set, it will be set to the default app.
        """
        super().__init__()
        self.app = getattr(settings, "PROCRASTINATE_APP", None)

        if self.app is None:
            from procrastinate.contrib.django import app

            self.app = app

    def check_status(self):
        """
        Use the built-in healthchecks to check if the Procrastinate app is
        working.
        """
        from procrastinate.contrib.django.healthchecks import healthchecks
        from procrastinate import exceptions

        try:
            async_to_sync(healthchecks)(app=self.app)
        except exceptions.ConnectorException:
            self.add_error(
                ServiceUnavailable("Error connecting to Procrastinate database")
            )
        except Exception as exc:
            self.add_error(ServiceUnavailable("Error checking Procrastinate"), exc)


class ProcrastinateHealthCheck(DjangoHealthCheckWrapper):
    """
    Validates that Procrastinate is working and replying.
    """

    base_class = ProcrastinateBuiltInHealthCheck

    def get_name(self) -> str:
        return "Procrastinate Built-In Health Check"

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; Procrastinate cannot be reached

This test verifies several components of the Procrastinate system:

    1. Database connection - Ensures the system can connect to the database
    2. Migration status - Checks that all required migrations for the procrastinate app have been applied
    3. Default Django Procrastinate App - Verifies the default app can connect properly
    4. Worker App - Confirms the worker app can establish a connection

## Possible causes

    - Database connectivity issues (network problems, credentials, database server down)
    - Missing migrations for the procrastinate application
    - Configuration issues with either the default Django Procrastinate App or the Worker App

## Possible solutions

    - Check database server status and network connectivity
    - Run python manage.py migrate procrastinate to apply any missing migrations
    - Verify database credentials and connection settings
    - Check database permissions for the application user
    - Review logs for specific error messages that might indicate configuration problems
    - Ensure the database has enough resources (connections, memory, etc.) to handle requests
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["procrastinate_worker"]
