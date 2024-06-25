@smoke
Feature: Smoke test for the site

    As a developer,
    I want to see the site working,
    So that I know the application is not down.

    Scenario: Shows correct Django admin page
        Given I am logged in as a Django admin
        Then I should see the text "welcome"
        And I should not see the text "log in"
        And I should be at the URL "http://localhost:3001/back/admin/"
        And I should see the following Django admin models:
            | Group name                       | Model name    |
            | Authentication and Authorization | Groups        |

    Scenario Outline: Needs correct log in to access Django admin
        Given I am on the /back/admin page
        When I log in with <username> and <password>
        Then I should see the text "<expected_text>"
        And I should not see the text "<not_expected_text>"

        Examples:
            | username      | password  | expected_text            | not_expected_text        |
            | good@user.com | correct   | welcome                  | Please enter the correct |
            | good@user.com | incorrect | Please enter the correct | welcome                  |
            | bad@user.com  | correct   | Please enter the correct | welcome                  |

    Scenario: Non-admin user can't log in to Django admin
        Given I am the following user:
            | email    | good2@user.com |
            | is_admin | no             |
            | password | correct        |
        And I am on the /back/admin page
        When I log in with good2@user.com and correct
        Then I should see the text "Please enter the correct email address and password for a staff account"


