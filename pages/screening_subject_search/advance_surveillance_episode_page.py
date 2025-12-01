from playwright.sync_api import Page
from pages.screening_subject_search.advance_episode_page import AdvanceEpisodePage


class AdvanceSurveillanceEpisodePage(AdvanceEpisodePage):
    """Advance Surveillance Episode Page locators, and methods for interacting with the page."""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        
        # Locators
        self.discharge_from_surveillance_clinical_decision_button = self.page.get_by_role(
            "button", name="Discharge from Surveillance - Clinical Decision"
        )

    def click_discharge_from_surveillance_clinical_decision_button(self) -> None:
        """Click on the 'Discharge from Surveillance - Clinical Decision' button."""
        self.click(self.discharge_from_surveillance_clinical_decision_button)
