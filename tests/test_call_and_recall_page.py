import pytest
from sys import platform
from playwright.sync_api import Page, expect
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
    if platform == "win32": # File path from content root is required on Windows OS
        with open('tests/bcss_tests.properties', 'rb') as read_prop:
            configs.load(read_prop)
    elif platform == "darwin": # Only the filename is required on macOS
        with open('bcss_tests.properties', 'rb') as read_prop:
            configs.load(read_prop)
    return configs.properties


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as the specified user and navigates to the call and recall page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to call and recall page
    MainMenu(page).go_to_call_and_recall_page()


@pytest.mark.smoke
def test_call_and_recall_page_navigation(page: Page) -> None:
    """
    Confirms that the Call and Recall menu displays all menu options and confirms they load the correct pages
    """
    # Planning and monitoring page loads as expected
    page.get_by_role("link", name="Planning and Monitoring").click()
    expect(page.locator("#page-title")).to_contain_text("Invitations Monitoring - Screening Centre")
    page.get_by_role("link", name="Back").click()

    # Generate invitations page loads as expected
    page.get_by_role("link", name="Generate Invitations").click()
    expect(page.locator("#ntshPageTitle")).to_contain_text("Generate Invitations")
    page.get_by_role("link", name="Back").click()

    # Invitation generation progress page loads as expected
    page.get_by_role("link", name="Invitation Generation Progress").click()
    expect(page.locator("#ntshPageTitle")).to_contain_text("Invitation Generation Progress")
    page.get_by_role("link", name="Back").click()

    # Non invitation days page loads as expected
    page.get_by_role("link", name="Non Invitation Days").click()
    expect(page.locator("#ntshPageTitle")).to_contain_text("Non-Invitation Days")
    page.get_by_role("link", name="Back").click()

    # Age extension rollout page loads as expected
    page.get_by_role("link", name="Age Extension Rollout Plans").click()
    expect(page.locator("#page-title")).to_contain_text("Age Extension Rollout Plans")
    page.get_by_role("link", name="Back").click()

    # Return to main menu
    page.get_by_role("link", name="Main Menu").click()
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")


def test_view_an_invitation_plan(page: Page, tests_properties: dict) -> None:
    """
    Confirms that an invitation plan can be viewed via a screening centre from the planning ad monitoring page
    """
    # Go to planning and monitoring page
    page.get_by_role("link", name="Planning and Monitoring").click()

    # Select a screening centre
    page.get_by_role("link", name=tests_properties["screening_centre_code"]).click()

    # Select an invitation plan
    page.get_by_role("row").nth(1).get_by_role("link").click()

    # Verify invitation page is displayed
    expect(page.locator("#page-title")).to_contain_text("View a plan")
