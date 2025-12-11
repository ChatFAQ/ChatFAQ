import contextlib
import io
import logging
from typing import Mapping, Sequence

from asgiref.sync import async_to_sync
from django.conf import settings
from health_check.cache.backends import CacheBackend
from health_check.db.backends import (
    BaseHealthCheckBackend,
    DatabaseBackend,
    ServiceUnavailable,
)

from .base import DjangoHealthCheckWrapper, HealthCheck, Outcome, Status
from .models import Event

# Get a logger instance
logger = logging.getLogger(__name__)


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
        from procrastinate import exceptions
        from procrastinate.contrib.django.healthchecks import healthchecks

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


class ModuleSimulationBase(HealthCheck):
    """
    Base class for module simulation health checks.
    Checks the status by looking at the results of the last periodic task run.
    """

    MODULE_NUMBER = None
    MODULE_NAME = None
    WINDOW = dict(hours=7)

    def get_name(self) -> str:
        return f"{self.MODULE_NAME} Simulation"


    def get_status(self) -> Outcome:
        """
        Checks the status of the module simulation based on the latest event
        recorded by the periodic Procrastinate task.
        """
        event_type = f"module_{self.MODULE_NUMBER}_simulation"
        stats = Event.objects.type(event_type).within(**self.WINDOW).stats()
        stats_str = disp_stats(stats)

        if stats["total"] == 0:
            # No events found, means the task likely didn't run
            outcome = dict(
                status=Status.ERROR,
                message=f"No simulation task events found in the last {disp_window(self.WINDOW)}",
            )
        elif stats["failure"]:
            outcome = dict(
                status=Status.ERROR,
                message=f"{stats_str} in the last {disp_window(self.WINDOW)}",
            )
        else:
            outcome = dict(
                status=Status.OK,
                message=f"{stats_str} in the last {disp_window(self.WINDOW)}",
            )

        return Outcome(
            instance=self,
            **outcome,
        )

    def get_resolving_actions(self, outcome: Outcome) -> str:
        # Adjust the explanation slightly
        return f"""# __CODE__ &mdash; {self.MODULE_NAME} Simulation Task Failed or Delayed

This check verifies the status of the last background task run for the {self.MODULE_NAME} simulation.
The background task simulates a file generation via WebSocket to verify:
- The WebSocket server is reachable.
- The FSM works correctly.
- The FastAPI modules server is reachable.
- The file generation LLM is reachable.
- The file storage is reachable.

## Possible Causes for ERROR/WARNING:

- **Network Connectivity:** Issues connecting to the WebSocket server, module server, LLM, or storage.
- **Base File Missing:** The required input file (`health_check_files/...`) might be missing from storage.
- **Module/FSM Logic Error:** An error within the specific module's logic or the FSM definition.
- **Resource Exhaustion:** The simulation task might be timing out due to resource limits (CPU, RAM).
- The LLM API keys might be invalid or the LLM provider is down.
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return ["fsm", "module server"]


class Module1Simulation(ModuleSimulationBase):
    """
    Simulates a file generation with module 1 of the chatbot to check if
    WebSocket connection, message processing and file generation are working correctly.
    """

    MODULE_NUMBER = 1
    MODULE_NAME = "Info2ArticleXia"


class Module2Simulation(ModuleSimulationBase):
    """
    Simulates a file generation with module 2 of the chatbot to check if
    WebSocket connection, message processing and file generation are working correctly.
    """

    MODULE_NUMBER = 2
    MODULE_NAME = "TopicsIndexGenXia"


class Module3Simulation(ModuleSimulationBase):
    """
    Simulates a file generation with module 3 of the chatbot to check if
    WebSocket connection, message processing and file generation are working correctly.
    """

    MODULE_NUMBER = 3
    MODULE_NAME = "ColAgreeSumXia"


class LLMCheck(HealthCheck):
    """
    Validates that the enabled LLM are working correctly.
    """

    WINDOW = dict(hours=1)

    def get_name(self) -> str:
        return "LLM Check"

    def get_status(self) -> Outcome:
        events = Event.objects.types(["llm_call_complete", "llm_call_start"]).within(
            **self.WINDOW
        )
        stats = events.stats()
        stats_str = disp_stats(stats)

        if stats["failure"]:
            errors = [e.data for e in events.filter(is_success=False)]
            return Outcome(
                instance=self,
                status=Status.ERROR,
                message=f"{stats_str} in the last {disp_window(self.WINDOW)}",
                extra={"errors": errors},
            )
        else:
            return Outcome(
                instance=self,
                status=Status.OK,
                message=f"{stats_str} in the last {disp_window(self.WINDOW)}",
            )

    def get_resolving_actions(self, outcome: Outcome) -> str:
        return """# __CODE__ &mdash; LLM failed

This check validates that the enabled LLM are working correctly.

## Possible causes

- The API key is invalid.
- The defined endpoint url is invalid.
- The model provider is down.
"""

    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        return []
