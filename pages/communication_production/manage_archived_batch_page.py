from playwright.sync_api import Page
from pages.base_page import BasePage
from playwright.sync_api import expect


class ManageArchivedBatchPage(BasePage):
    """Page object for the Manage Archived Batch Screen."""

    def __init__(self, page: Page):
        super().__init__(page)

    def assert_batch_details_visible(self) -> None:
        """Verifies the Manage Archived Batch page has loaded."""
        header = self.page.locator("#page-title")
        expect(header).to_have_text("Manage Archived Batch")
