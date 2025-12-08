from playwright.sync_api import Page
from pages.base_page import BasePage


class MaintainAnalysersPage(BasePage):
    """Maintain Analysers page locators and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Maintain Analysers - page locators, methods
        self.analysers_table = page.locator("#analyserTableDiv")
        self.create_new_analyser_button = page.get_by_role(
            "button", name="Create New Analyser"
        )

    def verify_maintain_analysers_title(self) -> None:
        """Verify the Maintain Analysers page title is displayed correctly."""
        self.bowel_cancer_screening_page_title_contains_text("Maintain Analysers")
