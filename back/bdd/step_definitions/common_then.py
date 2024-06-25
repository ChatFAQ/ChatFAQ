"""
These are the common then steps that can be used in scenarios.

- Then steps represent the assertions
"""

import re

from playwright.sync_api import ConsoleMessage, Page, expect
from pytest_bdd import parsers, then

from . import utils


@then(parsers.cfparse('the text "{text}" should be the colour "{colour}"'))
def text_should_be_colour(page: Page, text: str, colour: str):
    """
    A bit of hubris, but the point being to test that the Nuxt injection
    of the Wagtail served content is working as expected.

    Also a good example of how you can test inside the JS of a page
    """
    element = page.get_by_text(text)
    colour = colour.lower()

    actual_colour = element.evaluate(
        """(element) => {
        const style = window.getComputedStyle(element)
        return style.color
        }"""
    )

    assert (
        actual_colour == colour
    ), f"Actual colour: {actual_colour}, Expected colour: {colour}"


@then(parsers.cfparse('I should be at the URL "{url}"'))
def at_exact_url(url: str, page: Page):
    """
    Checks the current URL for an exact match

    Example:
    ```gherkin
        Then I should be at the URL "https://example.com"
        Then I should be at the URL "http://localhost:3000/me"
        Then I should be at the URL "http://localhost:3000/me?q=1"
    ```
    """
    expect(page).to_have_url(url)


@then(parsers.cfparse('I should be at a URL with "{url}"'))
def at_partial_url(url: str, page: Page):
    """
    Checks the current URL for a partial match

    Example:
    ```gherkin
        Then I should be at a URL with "example.com"
        Then I should be at a URL with "me"
        Then I should be at a URL with "q=1"
    ```
    """
    expect(page).to_have_url(re.compile(f".*{url}.*"))


@then(parsers.cfparse('I should see the "{data_testid}"'))
@then(parsers.cfparse('I should see "{data_testid}"'))
def should_see_element(data_testid: str, page: Page):
    """Checks the page for an element with the expected element with data-testid"""
    expect(page.get_by_test_id(data_testid)).to_be_visible()


@then(parsers.cfparse('I should not see the "{data_testid}"'))
@then(parsers.cfparse('I should not see "{data_testid}"'))
def should_not_see_element(data_testid: str, page: Page):
    """Checks that the page does not contain the expected element with data-testid"""
    expect(page.get_by_test_id(data_testid)).not_to_be_visible()


@then(parsers.cfparse('I should see the text "{text}"'))
@then(parsers.cfparse('I should see the "{text}" message'))
def should_see_text(page: Page, text: str):
    """Checks the page for the expected text"""
    expect(page.get_by_text(text)).to_be_visible()


@then(parsers.cfparse('I should not see the text "{text}"'))
@then(parsers.cfparse('I should not see the "{text}" message'))
def should_not_see_text(page: Page, text: str):
    """Checks the page to make sure the expected text is not visible"""
    expect(page.get_by_text(text)).not_to_be_visible()


@then(parsers.cfparse("the {data_testid} should contain the text: {text}"))
@then(parsers.cfparse("{data_testid} should contain the text: {text}"))
def element_should_contain_text(data_testid: str, text: str, page: Page):
    """Checks the text of an element with the expected data-testid"""
    expect(page.get_by_test_id(data_testid)).to_have_text(text)


@then("I should see no console errors")
def should_see_no_console_errors(page: Page, console: ConsoleMessage):
    """
    Checks the console for any errors
    """
    errors = [msg.text for msg in console if msg.type == "error"]
    assert not errors, f"Console errors: {errors}"


@then(parsers.cfparse("I should see the following Django admin models:\n{datatable}"))
def should_see_admin_models(page: Page, datatable):
    """
    Checks the page for the expected admin models

    Example:
    ```gherkin
        Then I should see the following admin models:
            | Group name                       | Model name    |
            | Authentication and Authorization | Groups        |
            | Celery Results                   | Group Results |
    ```
    """
    datatable = utils.parse_datatable_string(datatable)
    for row in datatable:
        group_name = row["Group name"]
        model_name = row["Model name"]

        # Find the caption element with the specified text
        group_caption = page.locator("caption").get_by_text(group_name)
        expect(group_caption).to_be_visible()

        # Find the parent table element containing the caption
        model_table = page.locator("table").filter(has=group_caption)
        expect(model_table).to_be_visible()

        # Find the model element within the table
        model_element = model_table.locator("a").get_by_text(model_name)
        expect(model_element).to_be_visible()
