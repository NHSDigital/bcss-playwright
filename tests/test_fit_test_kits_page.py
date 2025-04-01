import pytest
from playwright.sync_api import Page, expect
from utils.click_helper import click
from pages.base_page import BasePage
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    fit test kits page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to fit test kits page
    BasePage(page).go_to_fit_test_kits_page()


@pytest.mark.smoke
def test_fit_test_kits_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the fit test kits page, and that the relevant pages
    are loaded when the links are clicked
    """
    # Verify FIT rollout summary page opens as expected
    click(page, page.get_by_role("link", name="FIT Rollout Summary"))
    expect(page.locator("body")).to_contain_text("FIT Rollout Summary")
    click(page, page.get_by_role("link", name="Back"))

    # Verify Log Devices page opens as expected
    click(page, page.get_by_role("link", name="Log Devices"))
    expect(page.locator("#page-title")).to_contain_text("Scan Device")
    click(page, page.get_by_role("link", name="Back"))

    # Verify View FIT Kit Result page opens as expected
    click(page, page.get_by_role("link", name="View FIT Kit Result"))
    expect(page.locator("body")).to_contain_text("View FIT Kit Result")
    click(page, page.get_by_role("link", name="Back"))

    # Verify Kit Service Management page opens as expected
    click(page, page.get_by_role("link", name="Kit Service Management"))
    expect(page.locator("#page-title")).to_contain_text("Kit Service Management")
    click(page, page.get_by_role("link", name="Back"))

    # Verify Kit Result Audit page opens as expected
    click(page, page.get_by_role("link", name="Kit Result Audit"))
    expect(page.locator("#page-title")).to_contain_text("Kit Result Audit")
    click(page, page.get_by_role("link", name="Back"))

    # Verify View Algorithm page opens as expected
    click(page, page.get_by_role("link", name="View Algorithm"))
    expect(page.locator("body")).to_contain_text("Select Algorithm")
    click(page, page.get_by_role("link", name="Back"))

    # Verify View Screening Centre FIT page opens as expected
    click(page, page.get_by_role("link", name="View Screening Centre FIT"))
    expect(page.locator("body")).to_contain_text("Select Screening Centre")
    click(page, page.get_by_role("link", name="Back"))

    # Verify Screening Incidents List page opens as expected
    click(page, page.get_by_role("link", name="Screening Incidents List"))
    expect(page.locator("#page-title")).to_contain_text("Screening Incidents List")
    click(page, page.get_by_role("link", name="Back"))

    # Verify FIT QC Products page opens as expected
    click(page, page.get_by_role("link", name="Manage QC Products"))
    expect(page.locator("#page-title")).to_contain_text("FIT QC Products")
    click(page, page.get_by_role("link", name="Back"))

    # Verify Maintain Analysers page opens as expected
    click(page, page.get_by_role("link", name="Maintain Analysers"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Maintain Analysers")
    click(page, page.get_by_role("link", name="Back"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("FIT Test Kits")

    # Return to main menu
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")
