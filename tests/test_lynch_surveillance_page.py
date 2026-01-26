import random
from typing import Generator
import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.lynch_surveillance.lynch_invitation_page import LynchInvitationPage
from pages.lynch_surveillance.set_lynch_invitation_rates_page import (
    SetLynchInvitationRatesPage,
)
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    lynch surveillance page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Go to Lynch Surveillance page
    BasePage(page).go_to_lynch_surveillance_page()


@pytest.fixture
def reset_lynch_invitation_rate(page: Page) -> Generator[None, None, None]:
    """
    Teardown fixture for resetting Lynch invitation Rates to environment defaults
    """
    yield
    page.get_by_role("link", name="Main Menu").click()
    BasePage(page).go_to_page(["Lynch Surveillance", "Set Lynch Invitation Rates"])
    set_lynch_invitation_rate_page = SetLynchInvitationRatesPage(page)
    set_lynch_invitation_rate_page.set_lynch_invitation_rate("2", "10")
    set_lynch_invitation_rate_page.set_lynch_invitation_rate("3", "5")
    set_lynch_invitation_rate_page.click_set_rates()


@pytest.mark.smoke
def test_lynch_surveillance_page_navigation(page: Page) -> None:
    """
    Confirms that the 'set lynch invitation rates' link is visible and clickable, and navigates to the
    expected page when clicked
    """
    # 'Set lynch invitation rates' page loads as expected
    LynchInvitationPage(page).click_set_lynch_invitation_rates_link()
    SetLynchInvitationRatesPage(page).verify_set_lynch_invitation_rates_title()

    # Return to main menu
    BasePage(page).click_main_menu_link()
    BasePage(page).main_menu_header_is_displayed()


def test_set_lynch_invitation_rate(
    page: Page, reset_lynch_invitation_rate: None
) -> None:
    """
    Navigate to Lynch Surveillance Set Lynch Invitation Rates page, set random invitation rates for Wolverhampton and Coventry centres.
    Verify the rates are saved correctly by navigating back and checking the values match what was set.
    """

    LynchInvitationPage(page).go_to_page(["Set Lynch Invitation Rates"])

    set_lynch_invitation_rate_page = SetLynchInvitationRatesPage(page)

    wolverhampton_invitation_rate = str(random.randint(1, 9))
    coventry_invitation_rate = str(random.randint(1, 9))

    set_lynch_invitation_rate_page.set_lynch_invitation_rate(
        "2", wolverhampton_invitation_rate
    )
    set_lynch_invitation_rate_page.set_lynch_invitation_rate(
        "3", coventry_invitation_rate
    )
    set_lynch_invitation_rate_page.click_set_rates()

    page.get_by_role("link", name="Back").click()
    page.get_by_role("link", name="Set Lynch Invitation Rates").click()
    expect(set_lynch_invitation_rate_page.get_lynch_invitation_rate("2")).to_have_value(
        wolverhampton_invitation_rate
    )
    expect(set_lynch_invitation_rate_page.get_lynch_invitation_rate("3")).to_have_value(
        coventry_invitation_rate
    )
