from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LetterLibraryIndexPage(BasePage):
    """Letter Library Index Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Letter Library Index - page locators, methods

    def verify_letter_library_index_title(self) -> None:
        """Verify the Letter Library Index page title is displayed as expected"""
        self.bowel_cancer_screening_page_title_contains_text("Letter Library Index")
