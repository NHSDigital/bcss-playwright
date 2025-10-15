from playwright.sync_api import Page
from pages.base_page import BasePage
import logging


class SubjectPage(BasePage):
    """Page object for interacting with subject-related actions."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    class TestData:
        hub_manager_role = "Hub Manager"
        lynch_diagnosis_type = "EPCAM"
        subject_age = 75
        diagnosis_date = "3 years ago"
        last_colonoscopy_date = "2 years ago"
        screening_status_lynch_self_referral = "Lynch Self-referral"

    def self_refer_subject(self) -> None:
        """Implement UI steps to self-refer the subject."""
        logging.warning("[TODO] self_refer_subject not yet implemented.")
        # TODO: Implement UI steps to self-refer the subject

    def set_seeking_further_data(self) -> None:
        """Set the subject to Seeking Further Data."""

        logging.info(
            "[UI ACTION] Setting screening status to 'Seeking Further Data' with reason 'Uncertified Death'"
        )

        # Select 'Seeking Further Data' from the screening status dropdown
        self.page.get_by_label("Change Screening Status").select_option(
            "4007"
        )  # Seeking Further Data

        # Select 'Uncertified Death' as the reason
        self.page.get_by_label("Reason", exact=True).select_option(
            "11314"
        )  # Uncertified Death

        # Click the update button
        self.safe_accept_dialog(
            self.page.get_by_role("button", name="Update Subject Data")
        )

    def set_self_referral_screening_status(self) -> None:
        """Set the screening status to 'Lynch Self-referral' with reason 'Reset seeking further data to Lynch Self-referral'."""
        logging.info("[UI ACTION] Setting screening status to 'Lynch Self-referral'")

        # Select 'Lynch Self-referral' (value: 4005)
        self.page.get_by_label("Change Screening Status").select_option("4005")

        # Select reason: 'Reset seeking further data to Lynch Self-referral' (value: 11529)
        self.page.get_by_label("Reason").select_option("11529")

        # Click the update button
        self.page.get_by_role("button", name="Update Subject Data").click()

    def receive_lynch_diagnosis(
        self, diagnosis_type, age, diagnosis_date, last_colonoscopy_date=None
    ) -> None:
        """
        Simulates receiving a Lynch diagnosis for a subject via the UI.
        """
        logging.info(
            f"[UI ACTION] Receiving Lynch diagnosis: {diagnosis_type}, age={age}, diagnosis_date={diagnosis_date}, colonoscopy={last_colonoscopy_date}"
        )

        # Example UI interactions
        self.page.get_by_label("Diagnosis Type").select_option(diagnosis_type)
        self.page.get_by_label("Age").fill(str(age))
        self.page.get_by_label("Diagnosis Date").fill(diagnosis_date)

        if last_colonoscopy_date:
            self.page.get_by_label("Last Colonoscopy Date").fill(last_colonoscopy_date)

        self.page.get_by_role("button", name="Submit").click()
