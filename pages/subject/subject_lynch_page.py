from playwright.sync_api import Page
from pages.base_page import BasePage
import logging


class SubjectPage(BasePage):
    """Page object for interacting with subject-related actions."""

    class Locators:
        SCREENING_STATUS_DROPDOWN = "Change Screening Status"
        REASON_DROPDOWN = "Reason"
        UPDATE_BUTTON = "Update Subject Data"
        DIAGNOSIS_TYPE_DROPDOWN = "Diagnosis Type"
        AGE_INPUT = "Age"
        DIAGNOSIS_DATE_INPUT = "Diagnosis Date"
        LAST_COLONOSCOPY_DATE_INPUT = "Last Colonoscopy Date"
        SUBMIT_BUTTON = "Submit"

    class StatusCodes:
        """Status codes used in the screening status dropdown."""

        LYNCH_SELF_REFERRAL = "4005"
        SEEKING_FURTHER_DATA = "4007"

    class ReasonCodes:
        """Reason codes used in the reason dropdown."""

        SELF_REFERRAL = "11316"
        UNCERTIFIED_DEATH = "11314"
        RESET_TO_SELF_REFERRAL = "11529"

    class TestData:
        hub_manager_role = "Hub Manager"
        lynch_diagnosis_type = "EPCAM"
        subject_age = 75
        diagnosis_date = "3 years ago"
        last_colonoscopy_date = "2 years ago"
        screening_status_lynch_self_referral = "Lynch Self-referral"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    def self_refer_subject(self) -> None:
        """Perform UI steps to self-refer the subject."""
        logging.info("[UI ACTION] Self-referring the subject")

        # Select 'Lynch Self-referral' from the dropdown
        self.page.get_by_label(self.Locators.SCREENING_STATUS_DROPDOWN).select_option(
            self.StatusCodes.LYNCH_SELF_REFERRAL
        )

        # Select reason: 'Reset seeking further data to Lynch Self-referral'
        self.page.get_by_label(self.Locators.REASON_DROPDOWN).select_option(
            self.ReasonCodes.RESET_TO_SELF_REFERRAL
        )

        # Click the update subject data button
        self.safe_accept_dialog(
            self.page.get_by_role("button", name=self.Locators.UPDATE_BUTTON)
        )

    def set_seeking_further_data(self) -> None:
        """Set the subject to Seeking Further Data."""

        logging.info(
            "[UI ACTION] Setting screening status to 'Seeking Further Data' with reason 'Uncertified Death'"
        )

        # Select 'Seeking Further Data' from the screening status dropdown
        self.page.get_by_label(self.Locators.SCREENING_STATUS_DROPDOWN).select_option(
            self.StatusCodes.SEEKING_FURTHER_DATA
        )

        # Select 'Uncertified Death' as the reason
        self.page.get_by_label(self.Locators.REASON_DROPDOWN).select_option(
            self.ReasonCodes.UNCERTIFIED_DEATH
        )

        # Click the update button
        self.safe_accept_dialog(
            self.page.get_by_role("button", name=self.Locators.UPDATE_BUTTON)
        )

    def set_self_referral_screening_status(self) -> None:
        """Set the screening status to 'Lynch Self-referral' with reason 'Reset seeking further data to Lynch Self-referral'."""
        logging.info("[UI ACTION] Setting screening status to 'Lynch Self-referral'")

        # Select 'Lynch Self-referral'
        self.page.get_by_label(self.Locators.SCREENING_STATUS_DROPDOWN).select_option(
            self.StatusCodes.LYNCH_SELF_REFERRAL
        )

        # Select reason: 'Reset seeking further data to Lynch Self-referral'
        self.page.get_by_label(self.Locators.REASON_DROPDOWN).select_option(
            self.ReasonCodes.RESET_TO_SELF_REFERRAL
        )

        # Click the update button
        self.click(self.page.get_by_role("button", name=self.Locators.UPDATE_BUTTON))

    def receive_lynch_diagnosis(
        self, diagnosis_type, age, diagnosis_date, last_colonoscopy_date=None
    ) -> None:
        """
        Simulates receiving a Lynch diagnosis for a subject via the UI.
        """
        logging.info(
            f"[UI ACTION] Receiving Lynch diagnosis: {diagnosis_type}, age={age}, diagnosis_date={diagnosis_date}, colonoscopy={last_colonoscopy_date}"
        )

        # UI interactions
        self.page.get_by_label(self.Locators.DIAGNOSIS_TYPE_DROPDOWN).select_option(
            diagnosis_type
        )
        self.page.get_by_label(self.Locators.AGE_INPUT).fill(str(age))
        self.page.get_by_label(self.Locators.DIAGNOSIS_DATE_INPUT).fill(diagnosis_date)

        if last_colonoscopy_date:
            self.page.get_by_label(self.Locators.LAST_COLONOSCOPY_DATE_INPUT).fill(
                last_colonoscopy_date
            )

        self.click(self.page.get_by_role("button", name=self.Locators.SUBMIT_BUTTON))
