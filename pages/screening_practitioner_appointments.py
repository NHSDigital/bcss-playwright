from playwright.sync_api import Page
from pages.base_page import BasePage

class ScreeningPractitionerAppointmentsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # ScreeningPractitionerAppointments Page
        self.log_in_page = self.page.get_by_role("button", name="Log in")
        self.view_appointments_page = self.page.get_by_role("link", name="View appointments")
        self.patients_that_require_page = self.page.get_by_role("link", name="Patients that Require")

    def go_to_log_in_page(self)->None:
        self.click(self.log_in_page)

    def go_to_view_appointments_page(self)->None:
        self.click(self.view_appointments_page)

    def go_to_patients_that_require_page(self)->None:
        self.click(self.view_appointments_page)
