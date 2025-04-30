from playwright.sync_api import Page
from pages.base_page import BasePage


class ScreeningPractitionerDayView(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Screening Practitioner Day View   - page locators
        self.calendar_button = page.get_by_role("button", name="Calendar")
        self.practitioner_dropdown = self.page.locator("#UI_PRACTITIONER_NDV")

    def click_calendar_button(self) -> None:
        self.click(self.calendar_button)

    def click_patient_link(self, patient_name: str) -> None:
        self.click(self.page.get_by_role("link", name=patient_name))

    def select_practitioner_dropdown_option(self, practitioner: str | list) -> None:
        self.practitioner_dropdown.select_option(label=practitioner)
