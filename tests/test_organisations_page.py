import pytest
from sys import platform
from playwright.sync_api import Page, expect
from utils.click_helper import click
from pages.bcss_home_page import MainMenu
from utils.user_tools import UserTools
from jproperties import Properties


@pytest.fixture
def tests_properties() -> dict:
    """
    Reads the 'bcss_tests.properties' file and populates a 'Properties' object.
    Returns a dictionary of properties for use in tests.

    Returns:
        dict: A dictionary containing the values loaded from the 'bcss_tests.properties' file.
    """
    configs = Properties()
    if platform == "win32":  # File path from content root is required on Windows OS
        with open('tests/bcss_tests.properties', 'rb') as read_prop:
            configs.load(read_prop)
    elif platform == "darwin":  # Only the filename is required on macOS
        with open('bcss_tests.properties', 'rb') as read_prop:
            configs.load(read_prop)
    return configs.properties


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    organisations page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to organisations page
    MainMenu(page).go_to_organisations_page()


@pytest.mark.smoke
def test_organisations_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the organisations page, and that the relevant pages
    are loaded when the links are clicked
    """
    # Screening centre parameters page loads as expected
    click(page, page.get_by_role("link", name="Screening Centre Parameters"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Screening Centre Parameters")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # Organisation parameters page loads as expected
    click(page, page.get_by_role("link", name="Organisation Parameters"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("System Parameters")
    click(page, page.get_by_role("link", name="Back", exact=True))

    # Organisation and site details page loads as expected
    click(page, page.get_by_role("link", name="Organisation and Site Details"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Organisation and Site Details")
    click(page, page.get_by_role("link", name="Back"))

    # The links below are visible (not clickable due to user role permissions)
    expect(page.get_by_text("Upload NACS data (Bureau)")).to_be_visible()
    expect(page.get_by_text("Bureau", exact=True)).to_be_visible()

    # GP practice endorsement page loads as expected
    click(page, page.get_by_role("link", name="GP Practice Endorsement"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("GP Practice Endorsement")

    # Return to main menu
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")


def test_view_an_organisations_system_parameters(page: Page, tests_properties: dict) -> None:
    """
    Confirms that an organisation's system parameters can be accessed and viewed
    """
    # Go to screening centre parameters page
    click(page, page.get_by_role("link", name="Screening Centre Parameters"))

    # View an Organisation
    page.get_by_role("link", name=tests_properties["screening_centre_code"]).click()
    expect(page.locator("#ntshPageTitle")).to_contain_text("System Parameters")
