from playwright.sync_api import Page
from pages.base_page import BasePage


class RecordDiagnosisDatePage(BasePage):
    """Record Diagnosis Date Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Record Diagnosis Date - page locators
        self.diagnosis_date_field = self.page.locator("#diagnosisDate")

    def click_diagnosis_date_field(self) -> None:
        """Click the diagnosis date field."""
        self.click(self.diagnosis_date_field)
