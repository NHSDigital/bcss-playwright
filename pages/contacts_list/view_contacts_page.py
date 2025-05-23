from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ViewContactsPage(BasePage):
    """View Contacts Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # View Contacts - page locators
        self.view_contacts_title = self.page.locator("#ntshPageTitle")

    def verify_view_contacts_title(self) -> None:
        """Verify the View Contacts page title is displayed correctly"""
        BasePage(self.page).bowel_cancer_screening_page_title_contains_text(
            "View Contacts"
        )
