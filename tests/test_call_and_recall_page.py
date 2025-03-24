import pytest
from playwright.sync_api import Page, expect
from utils.click_helper import click
from pages.bcss_home_page import MainMenu
from pages.login_page import BcssLoginPage


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the call and recall page
    """
    # Log in to BCSS
    BcssLoginPage(page).login_as_user("BCSS401")

    # Go to call and recall page
    MainMenu(page).go_to_call_and_recall_page()


@pytest.mark.smoke
def test_call_and_recall_page_navigation(page: Page) -> None:
    """
    Confirms that the Call and Recall menu displays all menu options and confirms they load the correct pages
    """
    # Planning and monitoring page loads as expected
    click(page, page.get_by_role("link", name="Planning and Monitoring"))
    expect(page.locator("#page-title")).to_contain_text("Invitations Monitoring - Screening Centre")
    click(page, page.get_by_role("link", name="Back"))

    # Generate invitations page loads as expected
    click(page, page.get_by_role("link", name="Generate Invitations"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Generate Invitations")
    click(page, page.get_by_role("link", name="Back"))


    # Invitation generation progress page loads as expected
    click(page, page.get_by_role("link", name="Invitation Generation Progress"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Invitation Generation Progress")
    click(page, page.get_by_role("link", name="Back"))


    # Non invitation days page loads as expected
    click(page, page.get_by_role("link", name="Non Invitation Days"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Non-Invitation Days")
    click(page, page.get_by_role("link", name="Back"))

    # Age extension rollout page loads as expected
    click(page, page.get_by_role("link", name="Age Extension Rollout Plans"))
    expect(page.locator("#page-title")).to_contain_text("Age Extension Rollout Plans")
    click(page, page.get_by_role("link", name="Back"))


    # Return to main menu
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")


def test_view_an_invitation_plan(page: Page) -> None:
    """
    Confirms that an invitation plan can be viewed via a screening centre from the planning ad monitoring page
    """
    # Go to planning and monitoring page
    click(page, page.get_by_role("link", name="Planning and Monitoring"))

    # Select a screening centre
    click(page, page.get_by_role("link", name="BCS009"))

    # Select an invitation plan
    click(page, page.get_by_role("row").nth(1).get_by_role("link"))

    # Verify invitation page is displayed
    expect(page.locator("#page-title")).to_contain_text("View a plan")
