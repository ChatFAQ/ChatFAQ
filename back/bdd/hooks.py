"""
This file contains all the pytest-bdd hooks custom behaviour.

The hooks are used to extend the default pytest-bdd behaviour, such as adding
extra information to the JSON reporter such as screenshots and logs.
"""

import base64
from typing import Any, Callable

import pytest
from playwright.sync_api import Page
from pytest_bdd.parser import Feature, Scenario, Step
from slugify import slugify

from .report import utils as report_utils
from .report.reporter import Reporter
from .step_definitions import utils as step_utils

reporter = Reporter()


def get_datatable_from_step(step_name: str, step_func_args: Callable[..., Any]):
    """
    Extracts the datatable from the step function arguments to display
    it in the report nicely.

    We simply detect via a `\\n` in the step name, which only occurs when
    a datatable is present, but to get the correct orientation
    of the datatable, we use the step function argument name to detect it.

    If the argument is called `datatable_vertical`, we know it's a vertical
    datatable, otherwise it's a horizontal datatable.

    This way, if the naming convention is ignored, we still get OK results,
    just the header styling of table.
    """

    datatable_vertical = step_func_args.get("datatable_vertical")

    datatable = step_utils.get_datatable_from_step_name(step_name)

    if datatable:
        step_name = step_name.split("\n")[0]
        datatable = step_utils.parse_datatable_string(
            datatable, vertical=bool(datatable_vertical)
        )
        step_args = report_utils.datatable_to_arguments(datatable)
        reporter.update_existing_step(name=step_name, arguments=step_args)


def pytest_sessionstart() -> None:
    """
    Called before the test loop is started.

    We use this to initialize the reporter, which is used to store additional data
    """


def pytest_bdd_before_scenario(
    request: pytest.FixtureRequest,
    feature: Feature,
    scenario: Scenario,
) -> None:
    """
    Called before scenario is executed.
    We use this to keep track of which feature and scenario we are currently
    executing, so we can add the correct additional data to the correct scenario
    in the report.
    """

    reporter.start()

    if reporter.feature_uri != feature.rel_filename:
        reporter.feature_uri = feature.rel_filename
        reporter.increment_feature()

    reporter.increment_scenario()

    page: Page = request.getfixturevalue("page")

    reporter.update_existing_scenario(
        name=scenario.name,
        page=page,
    )


def pytest_bdd_before_step_call(
    request: pytest.FixtureRequest,
    feature: Feature,
    scenario: Scenario,
    step: Step,
    step_func: Callable[..., Any],
    step_func_args: dict[str, Any],
) -> None:
    """
    Called before step function is executed.
    We use this to keep track of which step we are currently executing,
    so we can add the correct additional data to the correct step in
    the report.
    """
    reporter.increment_step()
    get_datatable_from_step(step.name, step_func_args)


def pytest_bdd_after_step(
    request: pytest.FixtureRequest,
    feature: Feature,
    scenario: Scenario,
    step: Step,
    step_func: Callable[..., Any],
    step_func_args: dict[str, Any],
) -> None:
    """
    Called after step function is executed.
    We use this to prettify the datatable into a standard format cucumber json
    understands, but pytest-bdd does not currently support.

    In order to style the direction of the datatable correctly, we need to know
    if it's a vertical or horizontal datatable.  Therefore, we expect the step
    argument to be called "datatable" or "datatable_vertical".
    """


def pytest_bdd_after_scenario(
    request: pytest.FixtureRequest,
    feature: Feature,
    scenario: Scenario,
) -> None:
    """
    Called after scenario is executed successfully.
    We use this to add a After steps for video and screenshot.
    """

    reporter.add_after_step(
        media_directory=slugify(request.node.nodeid),
        keyword="Video",
    )
    reporter.add_after_step(
        media_directory=slugify(request.node.nodeid),
        keyword="Screenshot",
    )


def pytest_bdd_step_error(
    request: pytest.FixtureRequest,
    feature: Feature,
    scenario: Scenario,
    step: Step,
    step_func: Callable[..., Any],
    step_func_args: dict[str, Any],
    exception: Exception,
):
    """
    Called when a step fails.
    We use this to add a screenshot to the report at the failing step.
    """
    page = request.getfixturevalue("page")
    screenshot_bytes = page.screenshot(full_page=True)
    png = base64.b64encode(screenshot_bytes).decode()
    reporter.attach(png, "image/png")


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int | pytest.ExitCode,
) -> None:
    """
    Called after the entire session is finished.
    We use this to prepare the report by merging the additional data we want
    to include, and generating a HTML version.
    """
    if reporter.is_running:
        reporter.update_existing_steps_in_json()
        reporter.update_existing_scenarios_in_json()
        reporter.insert_embeddings_into_report()
        reporter.insert_additional_steps_into_report()
        reporter.generate_html_report()
