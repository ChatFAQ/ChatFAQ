"""
These are the common given steps that can be used in scenarios.

- Given steps represent the preconditions
"""

import httpx
from django.contrib.auth.models import AbstractBaseUser
from playwright.sync_api import Page
from pytest_bdd import given, parsers

from . import utils


@given(parsers.cfparse('I am at the URL "{url}"'))
def at_url(url: str, page: Page, front_server, live_server):
    """
    Go to the given URL

    Note: A map is used to introduce special URLs you may need.
          The idea being to do a string replacement for special URLs
          eg. the api server's URL (which is random during testing)

    Example:
        Given I am at the URL "https://example.com"
        Given I am at the URL "http://localhost:3000/me"
        Given I am at the URL "http://localhost:3000/me?q=1"
    """

    # Map special URLs as required, else use the supplied URL
    SPECIAL_URLS = {
        "<API_URL>": str(live_server),
        "<FRONT_URL>": str(front_server),
    }

    for key, value in SPECIAL_URLS.items():
        url = url.replace(key, value)

    page.goto(url)


@given(parsers.cfparse("I am on the {page_name} page"))
def on_page(page_name: str, page: Page, front_server):
    """
    Go to the given page

    Note: A map is used to introduce special page paths you may need.
          The idea being the feature files are easier to read
          eg. home should route to ""

    Example:
        Given I am on the home page
        Given I am on the about/me page
        Given I am on the about/me?q=1 page
    """
    # remove leading and trailing slashes for consistent handling
    page_name = page_name.strip("/")

    # Map special page names as required, else use the supplied page name
    SPECIAL_PAGE_NAMES = {
        "home": "",
    }
    page_name = SPECIAL_PAGE_NAMES.get(page_name, page_name)

    page_url = httpx.URL(front_server).join(f"/{page_name}")
    page.goto(str(page_url))


@given(parsers.cfparse("I am logged in as a CMS admin"))
def logged_in_as_cms_admin(page: Page, front_server):
    """
    Log in as an admin to the CMS
    """
    on_page("", page, front_server)
    page.locator('input[name="username"]').fill("good@user.com")
    page.locator('input[name="password"]').fill("correct")
    page.locator('button[type="submit"]').click()


@given(parsers.cfparse("I am logged in as a Django admin"))
def logged_in_as_django_admin(page: Page, front_server):
    """
    Log in as an admin to Django
    """
    on_page("back/admin", page, front_server)
    page.locator('input[name="username"]').fill("good@user.com")
    page.locator('input[name="password"]').fill("correct")
    page.locator('input[type="submit"]').click()


@given(parsers.cfparse("I am the following user:\n{datatable_vertical}"))
def the_following_user(datatable_vertical: str, django_user_model: AbstractBaseUser):
    """
    Create a user with the given details

    Note: we accept an is_admin field to create a superuser

    Example:
    ```gherkin
        Given I am the following user:
            | email    | good2@user.com |
            | password | correct        |
    ```
    """
    datatable = utils.parse_datatable_string(datatable_vertical, vertical=True)

    is_superuser = utils.cast_to_bool(datatable.pop("is_admin", ""))

    if is_superuser:
        django_user_model.objects.create_superuser(**datatable)
    else:
        django_user_model.objects.create_user(**datatable)
