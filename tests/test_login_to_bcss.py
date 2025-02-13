from os import environ

from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from pages.login import BcssLoginPage

load_dotenv()


def test_successful_login_to_bcss(page: Page) -> None:
    username = environ.get("BCSS_USERNAME")
    password = environ.get("BCSS_PASSWORD")
    login_page = BcssLoginPage(page)
    login_page.login(username, password)
    expect(page.locator("#ntshAppTitle")).to_contain_text("Bowel Cancer Screening System")


def test_login_to_bcss_with_invalid_username(page: Page) -> None:
    username = "zzzzzz"
    password = environ.get("BCSS_PASSWORD")
    login_page = BcssLoginPage(page)
    login_page.login(username, password)
    expect(page.locator("body")).to_contain_text("Incorrect username or password.")


def test_login_to_bcss_with_invalid_password(page: Page) -> None:
    username = environ.get("BCSS_USERNAME")
    password = "zzzzzz"
    login_page = BcssLoginPage(page)
    login_page.login(username, password)
    expect(page.locator("body")).to_contain_text("Incorrect username or password.")


def test_login_to_bcss_with_no_username_or_password(page: Page) -> None:
    username = ""
    password = ""
    login_page = BcssLoginPage(page)
    login_page.login(username, password)
    # Login should fail - verify that sign in button is still visible
    expect(page.get_by_role("button", name="submit")).to_be_visible()
