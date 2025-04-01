import pytest
from playwright.sync_api import Page, expect
from utils.click_helper import click
from pages.base_page import BasePage
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    gfob test kits page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered")

    # Go to gFOBT test kits page
    BasePage(page).go_to_gfob_test_kits_page()


@pytest.mark.smoke
def test_gfob_test_kit_page_navigation(page: Page) -> None:
    """
    Confirms all menu items are displayed on the gfob test kits page, and that the relevant pages
    are loaded when the links are clicked
    """
    # Test kit logging page opens as expected
    click(page, page.get_by_role("link", name="Test Kit Logging"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Test Kit Logging")
    click(page, page.get_by_role("link", name="Back"))

    # Test kit reading page opens as expected
    click(page, page.get_by_role("link", name="Test Kit Reading"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Test Kit Quality Control Reading")
    click(page, page.get_by_role("link", name="Back"))

    # View test kit result page opens as expected
    click(page, page.get_by_role("link", name="View Test Kit Result"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("View Test Kit Result")
    click(page, page.get_by_role("link", name="Back"))

    # Create qc kit page opens as expected
    click(page, page.get_by_role("link", name="Create QC Kit"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Create QC Kit")

    # Return to main menu
    click(page, page.get_by_role("link", name="Main Menu"))
    expect(page.locator("#ntshPageTitle")).to_contain_text("Main Menu")


def test_create_a_qc_kit(page: Page) -> None:
    """
    Confirms that a qc test kit can be created and that each of the dropdowns has an option set available for selection
    """
    # 'Reading' dropdown locators
    reading1dropdown = page.locator("#A_C_Reading_999_0_0")
    reading2dropdown = page.locator("#A_C_Reading_999_0_1")
    reading3dropdown = page.locator("#A_C_Reading_999_1_0")
    reading4dropdown = page.locator("#A_C_Reading_999_1_1")
    reading5dropdown = page.locator("#A_C_Reading_999_2_0")
    reading6dropdown = page.locator("#A_C_Reading_999_2_1")

    # Navigate to create QC kit page
    click(page, page.get_by_role("link", name="Create QC Kit"))

    # Select QC kit drop down options
    reading1dropdown.select_option("NEGATIVE")
    reading2dropdown.select_option("POSITIVE")
    reading3dropdown.select_option("POSITIVE")
    reading4dropdown.select_option("UNUSED")
    reading5dropdown.select_option("NEGATIVE")
    reading6dropdown.select_option("POSITIVE")

    # Click save
    click(page, page.get_by_role("button", name="Save Kit"))

    # Verify kit has saved
    expect(page.locator("th")).to_contain_text("A quality control kit has been created with the following values:")
