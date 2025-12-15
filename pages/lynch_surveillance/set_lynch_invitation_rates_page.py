import logging
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage


class SetLynchInvitationRatesPage(BasePage):
    """Set Lynch Invitation Rates Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Lynch Invitation Page - Links, methods

    def verify_set_lynch_invitation_rates_title(self) -> None:
        """Verifies that the Set Lynch Invitation Rates title is displayed."""
        self.bowel_cancer_screening_page_title_contains_text(
            "Set Lynch Surveillance Invitation Rates"
        )

    def get_lynch_invitation_rate(self, screening_centre_id: str) -> Locator:
        return self.page.locator(f'[id="{screening_centre_id}"]')

    def set_lynch_invitation_rate(self, screening_centre_id: str, rate: str) -> None:
        """
        set lynch invitation rate
        """
        self.get_lynch_invitation_rate(screening_centre_id).fill(rate)

        logging.info(f"input {rate } for screening centre id {screening_centre_id} ")

    def click_set_rates(self) -> None:
        self.page.get_by_role("button", name="Set Rates").click()
        expect(self.page.locator("#alert")).to_contain_text("×Successfully updated")
        logging.info("click set rates")
