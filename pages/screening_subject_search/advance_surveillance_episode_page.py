from playwright.sync_api import Page
from pages.screening_subject_search.advance_episode_page import AdvanceEpisodePage


class AdvanceSurveillanceEpisodePage(AdvanceEpisodePage):
    """Advance Surveillance Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Locators
        self.discharge_from_surveillance_clinical_decision_button = (
            self.page.get_by_role(
                "button", name="Discharge from Surveillance - Clinical Decision"
            )
        )
        self.discharge_from_screening_and_surveillance_clinical_decision_button = (
            self.page.get_by_role(
                "button",
                name="Discharge from Screening and Surveillance - Clinical Decision",
            )
        )
        self.book_surveillance_appointment_button = self.page.get_by_role(
            "button", name="Book Surveillance Appointment"
        )

    def click_discharge_from_surveillance_clinical_decision_button(self) -> None:
        """Click on the 'Discharge from Surveillance - Clinical Decision' button."""
        self.click(self.discharge_from_surveillance_clinical_decision_button)

    def click_discharge_from_screening_and_surveillance_clinical_decision_button(
        self,
    ) -> None:
        """Click on the 'Discharge from Screening and Surveillance - Clinical Decision' button."""
        self.click(
            self.discharge_from_screening_and_surveillance_clinical_decision_button
        )

    def click_book_surveillance_appointment_button(self) -> None:
        """Click on the 'Book Surveillance Appointment' button."""
        self.safe_accept_dialog(self.book_surveillance_appointment_button)
        self.page.wait_for_timeout(500)  # Timeout to allow subject to update on the DB.
