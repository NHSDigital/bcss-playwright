import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from pages.login_page import BcssLoginPage

@pytest.mark.smoke
def test_successful_login_to_bcss(page: Page) -> None:
    """
    Confirms that a user with valid credentials can log in to bcss
    """
    # Enter a valid username and password and click 'sign in' button
    BcssLoginPage(page).login_as_user("BCSS401")
    # Confirm user has successfully signed in and is viewing the bcss homepage
    expect(page.locator("#ntshAppTitle")).to_contain_text("Bowel Cancer Screening System")


def test_login_to_bcss_with_invalid_username(page: Page) -> None:
    """
    Confirms that a user with a valid password, and invalid username, can NOT log in to bcss
    """
    # Take environment variables from .env
    load_dotenv()
    # Set an invalid username
    username = "BCSSZZZ"
    # Retrieve valid password from .env file
    password = os.getenv("BCSS_PASS")
    # Enter valid password with an invalid username and click 'sign in' button
    BcssLoginPage(page).login(username, password)
    # Confirm error message is displayed
    expect(page.locator("body")).to_contain_text("Incorrect username or password.")


def test_login_to_bcss_with_invalid_password(page: Page) -> None:
    """
    Confirms that a user with a valid username, and invalid password, can NOT log in to bcss
    """
    # Enter a valid username with an invalid password and click 'sign in' button
    username = "BCSS401"
    password = "zzzzzz"
    BcssLoginPage(page).login(username, password)
    # Confirm error message is displayed
    expect(page.locator("body")).to_contain_text("Incorrect username or password.")


def test_login_to_bcss_with_no_username_or_password(page: Page) -> None:
    """
    Confirms that a user can NOT log in to bcss if no credentials are entered in the log in form
    """
    # At the login screen, leave the fields empty and click 'sign in' button
    username = ""
    password = ""
    BcssLoginPage(page).login(username, password)
    # Login should fail - verify that sign-in button is still visible
    expect(page.get_by_role("button", name="submit")).to_be_visible()
