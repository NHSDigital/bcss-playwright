from playwright.sync_api import Page
from pages.screening_subject_search.advance_episode_page import AdvanceEpisodePage


class AdvanceLynchSurveillanceEpisodePage(AdvanceEpisodePage):
    """Advance Lynch Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Locators
        self.review_suitability_for_lynch_surveillance_button = page.get_by_role(
            "button", name="Review suitability for Lynch Surveillance"
        )
        self.refer_for_clinician_review_button = page.get_by_role(
            "button", name="Refer for Clinician Review"
        )

    def click_review_suitability_for_lynch_surveillance_button(self) -> None:
        """Click on the 'Review suitability for Lynch Surveillance' button."""
        self.safe_accept_dialog(self.review_suitability_for_lynch_surveillance_button)
        self.page.wait_for_timeout(500)  # Timeout to allow subject to update on the DB.

    def click_refer_for_clinician_review_button(self) -> None:
        """Click on the 'Refer for Clinician Review' button."""
        self.safe_accept_dialog(self.refer_for_clinician_review_button)
