from playwright.sync_api import Page
from pages.base_page import BasePage


class SurveillancePage(BasePage):
    """Page object for navigating to and interacting with the Surveillance page."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Locators
        self.surveillance_patients_due_page = self.page.get_by_role(
            "link", name="Surveillance Patients Due"
        )
        self.produce_healthcheck_forms_page = self.page.get_by_role(
            "link", name="Produce Healthcheck Forms"
        )
        self.surveillance_patients_awaiting_action_page = self.page.get_by_role(
            "link", name="Surveillance Patients Awaiting Action"
        )
        self.accept_transfer_of_patient_responsibility_between_screening_centres_page = self.page.get_by_role(
            "link",
            name="Accept Transfer of Patient Responsibility Between Screening Centres",
        )
        self.manage_surveillance_review_cases_page = self.page.get_by_role(
            "link", name="Manage Surveillance Review Cases"
        )

    def go_to_surveillance_patients_due_page(self) -> None:
        """Click the Surveillance Page 'Surveillance Patients Due' link."""
        self.click(self.surveillance_patients_due_page)

    def go_to_produce_healthcheck_forms_page(self) -> None:
        """Click the Surveillance Page 'Produce Healthcheck Forms' link."""
        self.click(self.produce_healthcheck_forms_page)

    def go_to_surveillance_patients_awaiting_action_page(self) -> None:
        """Click the Surveillance Page 'Surveillance Patients Awaiting Action' link."""
        self.click(self.surveillance_patients_awaiting_action_page)

    def go_to_accept_transfer_of_patient_responsibility_between_screening_centres_page(
        self,
    ) -> None:
        """Click the Surveillance Page 'Accept Transfer of Patient Responsibility Between Screening Centres' link."""
        self.click(
            self.accept_transfer_of_patient_responsibility_between_screening_centres_page
        )

    def go_to_manage_surveillance_review_cases_page(self) -> None:
        """Click the Surveillance Page 'Manage Surveillance Review Cases' link."""
        self.click(self.manage_surveillance_review_cases_page)
