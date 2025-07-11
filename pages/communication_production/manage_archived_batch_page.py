from playwright.sync_api import Page
from pages.base_page import BasePage
from playwright.sync_api import expect


class ManageArchivedBatchPage(BasePage):
    """Page object for the Manage Archived Batch Screen."""

    def __init__(self, page: Page):
        super().__init__(page)

    def assert_archived_batch_details_visible(self) -> None:
        """Verifies the Manage Archived Batch page has loaded."""
        header = self.page.locator("#page-title")
        expect(header).to_have_text("Manage Archived Batch")

    def click_reprint_button(self) -> None:
        """Clicks the 'Reprint' button on the Archived Batch details page."""
        reprint_button = self.page.locator("input.ReprintButton[value='Reprint Batch']")
        expect(reprint_button).to_be_visible()
        reprint_button.click()

    def confirm_archived_message_visible(self) -> None:
        """Verifies that the batch was successfully archived and confirmation message is shown."""
        confirmation_msg = self.page.locator(
            'text="Batch Successfully Archived and Printed"'
        )
        expect(confirmation_msg).to_be_visible()
