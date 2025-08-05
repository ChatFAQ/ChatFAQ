from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class Status(Enum):
    """
    Status of a health check.

    Attributes
    ----------
    OK
        The health check is OK, all is nominal.
    WARNING
        Some errors are detected but they should not prevent dependencies from
        being OK on their own (just maybe with less accuracy or performance).
    ERROR
        Some errors are detected and they prevent dependencies from being OK.
    """

    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @classmethod
    def choices(cls):
        """Choices for Django models"""

        return [(x.name, x.value) for x in cls]


@dataclass
class Outcome:
    """
    The outcome of a health check.

    Attributes
    ----------
    instance
        Instance of the health check we're looking at
    status
        The status of the health check.
    message
        A one-liner giving the status
    details
        Detailed explanation of what is wrong (in markdown, for display)
    """

    instance: "HealthCheck"
    status: Status
    message: str = ""
    details: str = ""
    extra: dict = field(default_factory=dict)


class HealthCheck(ABC):
    """
    Standard interface for a health check
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the display name
        """

        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> Outcome:
        """
        Makes the test and returns the outcome
        """

        raise NotImplementedError

    @abstractmethod
    def get_resolving_actions(self, outcome: Outcome) -> str:
        """
        Given an outcome, suggest a Markdown manual of how to resolve the
        issue. This will be shown to the user.

        Parameters
        ----------
        outcome
            Outcome from get_status()
        """

        raise NotImplementedError

    @abstractmethod
    def suggest_reboot(self, outcome: Outcome) -> Sequence[str]:
        """
        If this problem could be fixed by rebooting a component, which would it
        be?

        Parameters
        ----------
        outcome
            Outcome from get_status()
        """

        raise NotImplementedError

    def get_all_resolving_actions(self) -> Sequence[str]:
        """
        Default implementation that expects that the resolving action is
        independent from the outcome. If not, you'll have to override it.
        """

        # noinspection PyTypeChecker
        return [self.get_resolving_actions(None)]


class DjangoHealthCheckWrapper(HealthCheck, ABC):
    """
    Wrapper around the Django Health Check app, which already has some useful
    tests.
    """

    base_class = None

    def __init__(self):
        self.check = self.base_class()

    def get_status(self) -> Outcome:
        """
        We're running the test from Django Health Check and converting as best
        as possible.
        """

        self.check.run_check()
        return Outcome(
            instance=self,
            status=Status(Status.OK if self.check.status else Status.ERROR),
            message=self.check.pretty_status(),
            extra={"time_taken": self.check.time_taken},
        )
