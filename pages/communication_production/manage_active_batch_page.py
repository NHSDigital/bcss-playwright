from playwright.sync_api import Page
from pages.base_page import BasePage
from playwright.sync_api import expect


class ManageActiveBatchPage(BasePage):
    """Manage Active Batch Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Manage Active Batch - page buttons
        self.prepare_button = self.page.get_by_role("button", name="Prepare Batch")
        self.retrieve_button = self.page.get_by_role("button", name="Retrieve")
        self.confirm_button = self.page.get_by_role("button", name="Confirm Printed")
        # Manage Active Batch - page buttons (text)
        self.prepare_button_text = self.page.locator('text="Prepare Batch"')
        self.retrieve_button_text = self.page.locator('text="Retrieve"')
        self.confirm_button_text = self.page.locator('text="Confirm Printed"')
        self.reprepare_batch_text = self.page.locator('text="Re-Prepare Batch"')

    def click_prepare_button(self) -> None:
        """Click the Prepare Batch button"""
        self.click(self.prepare_button)

    def click_retrieve_button(self) -> None:
        """Click the Retrieve button"""
        self.click(self.retrieve_button)

    def click_confirm_button(self) -> None:
        """Click the Confirm Printed button"""
        self.click(self.confirm_button)

    def assert_batch_details_visible(self) -> None:
        """Asserts that the Manage Active Batch screen has loaded by checking the page title."""
        page_title = self.page.locator("#page-title")
        expect(page_title).to_have_text("Manage Active Batch")

