from playwright.sync_api import Page
from pages.base_page import BasePage


class SurveillancePage(BasePage):
    """Page object for navigating to and interacting with the Surveillance Pagesection."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Locators
        self.produce_healthcheck_forms = self.page.get_by_role('link', name='Produce Healthcheck Forms')
        

    def navigate_to_produce_healthcheck_forms(self):
        """Navigates to the Produce Healthcheck Forms section."""
        self.click(self.produce_healthcheck_forms)
        
