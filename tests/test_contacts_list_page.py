import pytest
from playwright.sync_api import Page, expect

from pages.contacts_list_page import ContactsListPage
from utils.click_helper import click
from pages.base_page import BasePage
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the contacts list page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to contacts list page
    BasePage(page).go_to_contacts_list_page()


@pytest.mark.smoke
def test_contacts_list_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the contacts list page, and that the relevant pages
    are loaded when the links are clicked
    """
    # View contacts page loads as expected
    click(page, page.get_by_role("link", name="View Contacts"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("View Contacts")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # Edit my contact details page loads as expected
    click(page, page.get_by_role("link", name="Edit My Contact Details"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Edit My Contact Details")
    click(page, page.get_by_role("link", name="Back"))

    # Maintain contacts page loads as expected
    click(page, page.get_by_role("link", name="Maintain Contacts"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Maintain Contacts")
    click(page, page.get_by_role("link", name="Back"))

    # My preference settings page loads as expected
    click(page, page.get_by_role("link", name="My Preference Settings"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("My Preference Settings")
    click(page, page.get_by_role("link", name="Back"))

    # Other links are visible (Not clickable due to user role permissions)
    expect(page.get_by_text("Extract Contact Details")).to_be_visible()
    expect(page.get_by_text("Resect and Discard Accredited")).to_be_visible()

    # Return to main menu
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")
