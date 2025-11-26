from playwright.sync_api import Page
from pages.base_page import BasePage


class ConfirmTheManualSendingOfADisclaimerLetterPage(BasePage):
    """Confirm The Manual Sending Of A Disclaimer Letter Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Confirm The Manual Sending Of A Disclaimer Letter - page locators
        self.confirm_button = self.page.get_by_role("button", name="Confirm")

    def click_confirm_button(self) -> None:
        """Click the 'Confirm' button."""
        self.click(self.confirm_button)
