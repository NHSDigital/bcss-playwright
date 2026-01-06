from playwright.sync_api import Page
from pages.fit_test_kits.create_new_analyser_page import CreateNewAnalyserPage


class EditAnalyserPage(CreateNewAnalyserPage):
    """Edit Analyser page locators and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    def verify_edit_analyser_title(self) -> None:
        """Verify the Edit Analyser page title is displayed correctly."""
        self.bowel_cancer_screening_page_title_contains_text("Edit Analyser")
