from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from enum import StrEnum


class DiagnosticTestOutcomePage(BasePage):
    """Diagnostic Test Outcome Page locators and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Diagnostic Test Outcome- page locators
        self.test_outcome_result = self.page.get_by_role(
            "cell", name="outcome_name"
        ).nth(1)
        self.test_outcome_dropdown = self.page.get_by_label(
            "Outcome of Diagnostic Test"
        )
        self.save_button = self.page.get_by_role("button", name="Save")

    def verify_diagnostic_test_outcome(self, outcome_name: str) -> None:
        """Verify that the diagnostic test outcome is visible."""
        expect(self.test_outcome_result(outcome_name)).to_be_visible()

    def select_test_outcome_option(self, option: str) -> None:
        """Select an option from the Outcome of Diagnostic Test dropdown."""
        self.outcome_dropdown.select_option(option)

    def click_save_button(self) -> None:
        """Click the 'Save' button."""
        self.click(self.save_button)


class OutcomeOfDiagnosticTest(StrEnum):
    """Enum for outcome of diagnostic test options."""

    Failed_Test_Refer_Another = "20363"
    Refer_Symptomatic = "20366"
    Refer_Surveillance = "20365"
