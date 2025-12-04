from playwright.sync_api import Page
from pages.screening_subject_search.advance_episode_page import AdvanceEpisodePage


class AdvanceFOBTScreeningEpisodePage(AdvanceEpisodePage):
    """Advance FOBT Screening Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.return_to_fobt_after_symptomatic_referral_button = self.page.get_by_role(
            "button", name="Return to FOBT after Symptomatic Referral"
        )

    def check_advance_checkbox(self) -> None:
        """Selects the 'Advance FOBT' checkbox"""
        self.advance_checkbox_label.check()

    def click_amend_diagnosis_date_button(self) -> None:
        """Checks the 'Advance FOBT' checkbox and clicks the 'Amend Diagnosis Date' button."""
        self.advance_checkbox_label_v2.check()
        self.click(self.amend_diagnosis_date_button)

    def click_return_to_fobt_after_symptomatic_referral_button(self) -> None:
        """Click the 'Return to FOBT after Symptomatic Referral' button."""
        self.safe_accept_dialog(self.return_to_fobt_after_symptomatic_referral_button)
