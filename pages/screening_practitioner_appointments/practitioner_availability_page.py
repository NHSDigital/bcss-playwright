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

    def select_royal_hospital_wolverhampton_dropdown_option (self) -> None:
        self.site_id_dropdown.select_option(label="THE ROYAL HOSPITAL (WOLVERHAMPTON)")  

    def select_astonish_ethanol_practitioner_dropdown_option (self) -> None:
        self.screening_practitioner_dropdown.select_option(label="Astonish, Ethanol")    

    def click_calendar_button (self) -> None:
        self.click(self.calendar_button)    
        