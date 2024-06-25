"""
This file adds fixtures related to reporting.
"""

import pytest

from ..report.reporter import Reporter


@pytest.fixture(scope="session", autouse=True)
def report() -> Reporter:
    """
    This fixture is used to create a session scoped report,
    which is used to store additional data to the cucumber report,
    such as screenshots and logs, and written to json at the end of the session.

    To use this fixture, simply add it as an argument in a step definition and then
    you can call the following methods:
    - attach(data: str, mime_type: str = "text/plain"): Attach a log to the current step.
    - attach_screenshot(page: Page, full_page: boolean = False): Attach a screenshot to the current step.

    Example:
    ```
    @given("I have a report")
    def i_have_a_report(report: Reporter, page: Page) -> None:
        report.attach("This is a log")
        report.attach_screenshot(page)
        report.attach_screenshot(page, full_page=True)
    ```
    """

    reporter = Reporter()

    return reporter
