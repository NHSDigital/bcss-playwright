import pytest
from playwright.sync_api import Page, expect
from pages.login_page import BcssLoginPage
from pages.base_page import BasePage
from utils.click_helper import click
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the communications
    production page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to communications production page
    BasePage(page).go_to_communications_production_page()


@pytest.mark.smoke
def test_communications_production_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the communications production page, and that the relevant pages
    are loaded when the links are clicked
    """
    # Active batch list page loads as expected
    click(page, page.get_by_role("link", name="Active Batch List"))
    expect(page.locator("#page-title")).to_contain_text("Active Batch List")
    click(page, page.get_by_role("link", name="Back"))

    # Archived batch list page loads as expected
    click(page, page.get_by_role("link", name="Archived Batch List"))
    expect(page.locator("#page-title")).to_contain_text("Archived Batch List")
    click(page, page.get_by_role("link", name="Back"))

    # Letter library index page loads as expected
    click(page, page.get_by_role("link", name="Letter Library Index"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Letter Library Index")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # Manage individual letter link is visible (not clickable due to user role permissions)
    expect(page.get_by_text("Manage Individual Letter")).to_be_visible()

    # Letter signatory page loads as expected
    click(page, page.get_by_role("link", name="Letter Signatory"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Letter Signatory")
    click(page, page.get_by_role("link", name="Back"))

    # Electronic communication management page loads as expected
    click(page, page.get_by_role("link", name="Electronic Communication"))
    expect(page.locator("#page-title")).to_contain_text("Electronic Communication Management")

    # Return to main menu
    # main_menu_link = page.get_by_role("link", name="Main Menu")
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")
