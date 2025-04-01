import pytest
from playwright.sync_api import Page, expect
from utils.click_helper import click
from pages.base_page import BasePage
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the download page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to download page
    BasePage(page).go_to_download_page()


@pytest.mark.smoke
def test_download_facility_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the downloads page, and that the relevant pages
    are loaded when the links are clicked. Also confirms that the warning header messages are displayed
    on the relevant pages
    """
    # Individual download request and retrieval page loads as expected
    click(page, page.get_by_role("link", name="Individual Download Request"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Individual Download Request and Retrieval")

    # Individual download request and retrieval page contains warning message
    expect(page.locator("form[name=\"frm\"]")).to_contain_text("Warning - FS Screening data will not be downloaded")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # List of Individual downloads page loads as expected
    click(page, page.get_by_role("link", name="List of Individual Downloads"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("List of Individual Downloads")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # Batch download request and retrieval page loads as expected
    click(page, page.get_by_role("link", name="Batch Download Request and"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Batch Download Request and Retrieval")

    # Batch download request and retrieval page contains warning message
    expect(page.locator("form[name=\"frm\"]")).to_contain_text("Warning - FS Screening data will not be downloaded")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # Return to main menu
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")
