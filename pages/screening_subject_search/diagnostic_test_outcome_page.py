import logging
from click import option
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from enum import StrEnum


class ReferralProcedureType(StrEnum):
    ENDOSCOPIC = "20356"
    RADIOLOGICAL = "20357"


class ReasonForOnwardReferral(StrEnum):
    CURRENTLY_UNSUITABLE_FOR_ENDOSCOPIC_REFERRAL = "20358"
    FURTHER_CLINICAL_ASSESSMENT = "20359"
    INCOMPLETE_COLONIC_VISUALISATION = "20481"


class DiagnosticTestOutcomePage(BasePage):
    """Diagnostic Test Outcome Page locators and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Diagnostic Test Outcome- page locators
        self.test_outcome_dropdown = self.page.get_by_label(
            "Outcome of Diagnostic Test"
        )
        self.save_button = self.page.get_by_role("button", name="Save")
        self.referral_procedure_dropdown = self.page.locator(
            "#UI_REFERRAL_PROCEDURE_TYPE"
        )
        self.reason_for_onward_referral_dropdown = self.page.locator("#UI_COMPLETE_ID")

    def verify_diagnostic_test_outcome(self, outcome_name: str) -> None:
        """
        Verify that the diagnostic test outcome is visible.

        Args:
            outcome_name (str): The accessible name or visible text of the test outcome cell to verify.
        """
        expect(self.page.get_by_role("cell", name=outcome_name).nth(1)).to_be_visible()

    def select_test_outcome_option(self, option: str) -> None:
        """Select an option from the Outcome of Diagnostic Test dropdown.

        Args:
            option (str): option (str): The option to select from the Outcome Of Diagnostic Test options.
        """
        self.test_outcome_dropdown.select_option(option)

    def click_save_button(self) -> None:
        """Click the 'Save' button."""
        self.click(self.save_button)

    def select_referral_procedure_type(self, value: ReferralProcedureType) -> None:
        """Select Radiological or Endoscopic Referral value."""
        self.referral_procedure_dropdown.wait_for(state="visible")
        self.referral_procedure_dropdown.select_option(value=value)

    def select_reason_for_onward_referral(self, value: ReasonForOnwardReferral) -> None:
        """Select Reason for Onward Referral value."""
        self.reason_for_onward_referral_dropdown.wait_for(state="visible")
        self.reason_for_onward_referral_dropdown.select_option(value=value)

    def select_first_valid_onward_referral_consultant(self) -> None:
        """Selects the first valid consultant from the lookup dropdown inside the iframe."""
        self.page.locator("#UI_CONSULTANT_PIO_SELECT_LINK").click()

        self.consultant_lookup_dropdown = self.page.frame_locator(
            "#UI_POPUP_wqggdxgaifr"
        ).locator("#UI_RESULTS_cgywrngg")

        self.consultant_lookup_dropdown.wait_for(state="visible")

        options = self.consultant_lookup_dropdown.locator("option").all()
        for option in options:
            value = option.get_attribute("value")
            if value:
                self.consultant_lookup_dropdown.click()  # Focus the dropdown
                self.consultant_lookup_dropdown.select_option(value=value)
                logging.info(f"Selected consultant with value: {value}")
                break


class OutcomeOfDiagnosticTest(StrEnum):
    """Enum for outcome of diagnostic test options."""

    FAILED_TEST_REFER_ANOTHER = "20363"
    REFER_SYMPTOMATIC = "20366"
    REFER_SURVEILLANCE = "20365"
    INVESTIGATION_COMPLETE = "20360"
    REFER_ANOTHER_DIAGNOSTIC_TEST = "20364"
