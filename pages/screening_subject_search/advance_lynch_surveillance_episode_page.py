from datetime import datetime
from playwright.sync_api import Page
from pages.screening_subject_search.advance_episode_page import AdvanceEpisodePage
from utils.calendar_picker import CalendarPicker


class AdvanceLynchSurveillanceEpisodePage(AdvanceEpisodePage):
    """Advance Lynch Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Locators
        self.review_suitability_for_lynch_surveillance_button = self.page.get_by_role(
            "button", name="Review suitability for Lynch Surveillance"
        )
        self.refer_for_clinician_review_button = self.page.get_by_role(
            "button", name="Refer for Clinician Review"
        )
        self.close_lynch_surveillance_episode_incorrect_diagnosis_button = (
            self.page.get_by_role(
                "button", name="Close Lynch Surveillance Episode (Incorrect Diagnosis)"
            )
        )
        self.close_lynch_surveillance_episode_clinical_reason_button = (
            self.page.get_by_role(
                "button", name="Close Lynch Surveillance Episode (Clinical Reason)"
            )
        )
        self.close_lynch_surveillance_episode_recent_colonsocopy_button = (
            self.page.get_by_role(
                "button", name="Close Lynch Surveillance Episode (Recent Colonoscopy)"
            )
        )
        self.last_colonoscopy_date_field = self.page.locator(
            "input[type='text'][id^='UI_APPT_DATE_']"
        )
        self.return_to_lynch_after_symptomatic_referral_button = self.page.get_by_role(
            "button", name="Return to Lynch after symptomatic referral"
        )

    def click_review_suitability_for_lynch_surveillance_button(self) -> None:
        """Click on the 'Review suitability for Lynch Surveillance' button."""
        self.safe_accept_dialog(self.review_suitability_for_lynch_surveillance_button)
        self.page.wait_for_timeout(500)  # Timeout to allow subject to update on the DB.

    def click_refer_for_clinician_review_button(self) -> None:
        """Click on the 'Refer for Clinician Review' button."""
        self.safe_accept_dialog(self.refer_for_clinician_review_button)

    def click_close_lynch_surveillance_episode_incorrect_diagnosis_button(self) -> None:
        """Click on the 'Close Lynch Surveillance Episode (Incorrect Diagnosis)' button."""
        self.safe_accept_dialog(
            self.close_lynch_surveillance_episode_incorrect_diagnosis_button
        )

    def click_close_lynch_surveillance_episode_clinical_reason_button(self) -> None:
        """Click on the 'Close Lynch Surveillance Episode (Clinical Reason)' button."""
        self.safe_accept_dialog(
            self.close_lynch_surveillance_episode_clinical_reason_button
        )

    def click_close_lynch_surveillance_episode_recent_colonsocopy_button(self) -> None:
        """Click on the 'Close Lynch Surveillance Episode (Recent Colonoscopy)' button."""
        self.safe_accept_dialog(
            self.close_lynch_surveillance_episode_recent_colonsocopy_button
        )

    def enter_lynch_last_colonoscopy_date(self, date: datetime) -> None:
        """Enter the Lynch Last Colonoscopy Date.

        Args:
            date (datetime): The date to enter.
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            date, self.last_colonoscopy_date_field
        )

    def click_return_to_lynch_after_symptomatic_referral_button(self) -> None:
        """Click on the 'Return to Lynch after symptomatic referral' button."""
        self.safe_accept_dialog(self.return_to_lynch_after_symptomatic_referral_button)
