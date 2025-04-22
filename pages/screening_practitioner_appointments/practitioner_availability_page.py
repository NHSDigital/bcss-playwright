from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.table_util import TableUtils


class PractitionerAvailabilityPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Practitioner Availability - page locators
        self.site_id_dropdown = page.locator("#UI_SITE_ID")
        self.screening_practitioner_dropdown = page.locator("#UI_PRACTITIONER_ID")
        self.calendar_button = page.get_by_role("button", name="Calendar")

    def select_site_dropdown_option(self, site_to_use: str) -> None:
        self.site_id_dropdown.select_option(label=site_to_use)

    def select_practitioner_dropdown_option(self, practitioner: str) -> None:
        self.screening_practitioner_dropdown.select_option(label=practitioner)

    def click_calendar_button(self) -> None:
        self.click(self.calendar_button)
