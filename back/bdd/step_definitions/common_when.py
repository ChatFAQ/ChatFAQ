"""
These are the common when steps that can be used in scenarios.

- When steps represent the actions steps

Note: Multiple regex patterns can be used on the same step, to make
      the feature files easier to read.
"""

from playwright.sync_api import Page
from pytest_bdd import parsers, when

from . import utils
from .common_given import at_url, on_page


@when(parsers.cfparse('I go to the URL "{url}"'))
def go_to_url(url: str, page: Page, front_server, live_server):
    at_url(url, page, front_server, live_server)


@when(parsers.cfparse("I visit the {page_name} page"))
def visit_page(page_name: str, page: Page, front_server):
    on_page(page_name, page, front_server)


@when(parsers.cfparse("I click {data_testid}"))
@when(parsers.cfparse("I click the {data_testid} button"))
@when(parsers.cfparse("I click the {data_testid} link"))
def click_on_data_testid(data_testid: str, page: Page):
    """
    Clicks the element with the data-testid attribute

    Example:
        When I click show more videos
        When I click the submit button
        When I click the my bookings link

        <button data-testid="show more videos">...
        <button data-testid="submit">...
        <a data-testid="my bookings">...
    """
    page.get_by_test_id(data_testid).click()


@when(parsers.cfparse('I enter "{value}" in {data_testid}'))
def fill_data_testid_with_value(data_testid: str, value: str, page: Page):
    """
    Enters the value into the input with the data-testid attribute

    Example:
        When I enter "chicken" in favourite sandwich

        <input data-testid="favourite sandwich" />
    """
    page.get_by_test_id(data_testid).fill(value)


@when(parsers.cfparse('I {data_testid} for "{value}"'))
def search_data_testid_for(data_testid: str, value: str, page: Page):
    """
    Enters the value into the input with the data-testid attribute
    and presses the enter key

    Example:
        When I search users for "John Doe"
        When I search cities for "New York"

        <input data-testid="search users" />
        <input data-testid="search cities" />
    """
    page.get_by_test_id(data_testid).fill(value)
    page.keyboard.press("Enter")


@when(parsers.cfparse("I submit the form with the following data:\n{datatable}"))
def fill_in_form_with_data(page: Page, datatable: str):
    """
    Fills in the form with the data provided.

    Example:
        When I submit the form with the following data:
        | age  | 25       |
        | name | John Doe |
        | city | New York |

    <input data-testid="age" />
    <input data-testid="name" />
    <input data-testid="city" />
    <button data-testid="submit" />
    """
    data = utils.parse_datatable_string(datatable, vertical=True)
    for key, value in data.items():
        page.get_by_test_id(key).fill(value)
    page.get_by_test_id("submit").click()


@when(parsers.cfparse("I log in with {username} and {password}"))
def log_in_with_username_and_password(username: str, password: str, page: Page):
    """
    Logs in with the username and password provided

    Example:
        When I log in with admin and password
    """
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)

    input_submit = page.locator('input[type="submit"]')
    button_submit = page.locator('button[type="submit"]')

    if input_submit.is_visible():
        input_submit.click()
    else:
        button_submit.click()
