import traceback
from dataclasses import dataclass, field
from collections.abc import Mapping, MutableMapping, Sequence

import networkx as nx
from sentry_sdk import capture_exception

from .checks import *
from .models import StatusHistory


@dataclass(frozen=True)
class Instance:
    """
    An instance of health check to be added to the graph
    """

    code: str = field(compare=True, hash=True)
    check: HealthCheck = field(compare=False, hash=False)
    depends_on: Sequence[str] = field(compare=False, hash=False)


@dataclass(frozen=True)
class Cause:
    """
    A cause for an issue (full output of a test, basically). If the test did
    not happen (for example because other tests failed before) then this will
    not contain an outcome.
    """

    instance: Instance
    outcome: Outcome | None

    @property
    def code(self):
        """Shortcut"""

        return self.instance.code

    @property
    def message(self):
        """Shortcut"""

        if not self.outcome:
            return ""

        return self.outcome.message

    @property
    def details(self):
        """Shortcut"""

        if not self.outcome:
            return ""

        return self.outcome.details

    @property
    def name(self):
        """Shortcut"""

        return self.instance.check.get_name()

    @property
    def resolving_actions(self):
        """Shortcut, with a bit of dirty templating"""

        if not self.outcome:
            return ""

        return self.instance.check.get_resolving_actions(self.outcome).replace(
            "__CODE__", self.code
        )

    def suggest_reboot(self) -> Sequence[str]:
        """Shortcut"""

        return self.instance.check.suggest_reboot(self.outcome)


class Resolver:
    """
    The goal of this class is to facilitate performing the checks and doing a
    root-cause analysis. We can know the root cause because we declare the
    dependencies between tests so if for example the queue stops responding
    then we'll skip checking the Celery workers.
    """

    def __init__(self):
        self.g = nx.DiGraph()
        self.instances: MutableMapping[str, Instance] = {}
        self.outcomes: Mapping[str, Outcome] = {}

    def register(self, instance: Instance):
        """
        Registering an instance. When all done, don't forget to build_graph()

        Parameters
        ----------
        instance
            Instance to register
        """

        self.instances[instance.code] = instance

    def build_graph(self):
        """
        Connects all dependencies through a networkx graph, which helps then
        sorting the graph in topological order.
        """

        for instance in self.instances.values():
            self.g.add_node(instance)

            for dependency in instance.depends_on:
                self.g.add_edge(self.instances[dependency], instance)

    def run_tests(self, stop_on_error=True):
        """
        We run the tests in topological order because if the root cause fails
        there is no need to fail all the dependent checks. There might be
        several root causes, but for now we'll simplify.

        Let's note that there is a stop_on_error flag. If it is set to False,
        we will run all the checks even if some of them fail. This is useful
        for debugging.
        """

        outcomes = {}

        for instance in nx.topological_sort(self.g):
            # noinspection PyBroadException
            try:
                status = instance.check.get_status()
            except Exception:
                capture_exception()
                traceback.print_exc()
                status = Outcome(instance, Status.ERROR, "(internal error)")

            outcomes[instance.code] = status

            if status.status == Status.ERROR and stop_on_error:
                break

        self.outcomes = outcomes

    def get_root_cause(self) -> Cause | None:
        """
        Once the tests are made (don't forget to run_tests()), determines the
        first failing test in topological order, which should be the root cause
        of the current malfunction (or at least one of the root cause(s)).

        Nothing is returned if everything is fine.
        """

        for instance in nx.topological_sort(self.g):
            outcome = self.outcomes[instance.code]
            if outcome.status == Status.ERROR:
                return Cause(instance, outcome)

    def check(self, stop_on_error=True) -> Cause | None:
        """
        Shortcut to run tests and get the root cause.

        Parameters
        ----------
        stop_on_error
            If you want to run all the tests despite the root cause being found
            you can set this to False.
        """

        self.run_tests(stop_on_error=stop_on_error)
        cause = self.get_root_cause()

        StatusHistory.log_status_change(cause)

        return cause

    def get_all_tests(self) -> Sequence[Cause]:
        """
        Returns all registered tests with their outcome
        """

        return [
            Cause(instance, self.outcomes.get(instance.code))
            for instance in nx.topological_sort(self.g)
        ]

    def get_all_resolving_actions(self) -> Sequence[str]:
        """
        Returns all resolving actions of all tests in topological order so that
        they can be put in the manual
        """

        for test in self.get_all_tests():
            # noinspection PyBroadException
            try:
                for action in test.instance.check.get_all_resolving_actions():
                    action = action.replace("__CODE__", test.code)

                    if action:
                        yield action
            except Exception:
                capture_exception()
                traceback.print_exc()
                pass

    def mermaid_graph(self) -> str:
        """
        Generates a Mermaid graph of the current system status
        """

        lines = ["flowchart TD"]

        for cause in self.get_all_tests():
            lines.append(f"    {cause.code}[{cause.code} - {cause.name}]")

            status = None

            if cause.outcome:
                status = cause.outcome.status

            if status == Status.OK:
                lines.append(f"    style {cause.code} fill:#dfe9e1,stroke:#4c7452")
            elif status == Status.WARNING:
                lines.append(f"    style {cause.code} fill:#fff1e0,stroke:#ae8b20")
            elif status == Status.ERROR:
                lines.append(f"    style {cause.code} fill:#f3dadd,stroke:#ae202e")
            else:
                lines.append(f"    style {cause.code} fill:#ebebeb,stroke:#3f3f3f")

            for dependency in self.g.predecessors(cause.instance):
                lines.append(f"    {dependency.code} --> {cause.code}")

        return "\n".join(lines)


def build_resolver() -> Resolver:
    """
    That's a shortcut to wire all the tests and their dependencies into a
    resolver.

    Rule for the codes:

    - I: Infrastructure
    - S: Self
    - E: External
    """

    resolver = Resolver()

    resolver.register(
        Instance(
            code="I001",
            check=Database(),
            depends_on=[],
        )
    )

    # :: IF api__redis

    resolver.register(
        Instance(
            code="I002",
            check=Cache(),
            depends_on=[],
        )
    )

    # :: ENDIF

    resolver.register(
        Instance(
            code="S001",
            check=RamUsage(),
            depends_on=[],
        )
    )

    resolver.register(
        Instance(
            code="S004",
            check=ProcrastinateHealthCheck(),
            depends_on=["I001"],
        )
    )

    resolver.build_graph()

    return resolver
