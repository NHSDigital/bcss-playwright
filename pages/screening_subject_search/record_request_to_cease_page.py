from playwright.sync_api import Page
from pages.base_page import BasePage
from enum import Enum
from utils.calendar_picker import CalendarPicker
from datetime import datetime
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.confirm_the_manual_sending_of_a_disclaimer_letter_page import (
    ConfirmTheManualSendingOfADisclaimerLetterPage,
)
from pages.screening_subject_search.record_informed_dissent_page import (
    RecordInformedDissentPage,
)
from typing import Optional


class RecordRequestToCeasePage(BasePage):
    """Record Request To Cease Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Record Request To Cease - page locators
        self.reason_dropdown = self.page.locator("#A_C_RequestCeaseReason")
        self.save_request_cease_button = self.page.get_by_role(
            "button", name="Save Request Cease"
        )
        self.confirm_cease_button = self.page.get_by_role(
            "button", name="Confirm Cease"
        )
        self.cease_notes = self.page.locator("#UI_NOTES_TEXT")
        self.cease_date_confirmed_textbox = self.page.locator(
            "#UI_CEASING_CONFIRM_DATE"
        )

    def select_request_cease_reason(self, cease_reason: "ReasonForCeasing") -> None:
        """
        Selects a request cease option.
        Args:
            cease_reason (ReasonForCeasing): The reason to request cease
        """
        self.reason_dropdown.select_option(label=cease_reason.reason)

    def click_save_request_cease_button(self) -> None:
        """Click the 'Save Request Cease' button."""
        self.click(self.save_request_cease_button)
        self.page.wait_for_timeout(
            500
        )  # Timeout to allow time for the subject to be updated on the DB.

    def fill_cease_notes(self, note: str) -> None:
        """
        Enter a Note in the cease notes
        Args:
            note (str): The note to add.
        """
        self.cease_notes.fill(note)

    def enter_cease_date_confirmed(self, date: datetime) -> None:
        """
        Enter cease date confirmed
        Args:
            date (datetime): The date to enter
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            date, self.cease_date_confirmed_textbox
        )

    def click_confirm_cease_button(self) -> None:
        """Click the 'Confirm Cease' button."""
        self.click(self.confirm_cease_button)

    def cease_subject_with_reason(self, reason: str) -> None:
        """
        Ceases a subject with a reason
        Args:
            reason (str): The reason to request cease:
                Can be any of the following:
                - Informed Dissent
                - Informed Dissent (verbal only)
                - No Colon (subject request)
                - No Colon (programme assessed)
                - Informal Death
        """
        reason_for_ceasing = ReasonForCeasing.by_description_case_insensitive(reason)
        if reason_for_ceasing is None:
            raise ValueError("Incorrect reason for cease selected.")
        self.select_request_cease_reason(reason_for_ceasing)

        if reason_for_ceasing.is_immediate_cease:
            self.fill_cease_notes("AUTO TESTING: confirm immediate manual cease")
            self.enter_cease_date_confirmed(datetime.now())
            self.click_confirm_cease_button()

        else:
            self.click_save_request_cease_button()
            SubjectScreeningSummaryPage(self.page).click_record_disclaimer_letter_sent()
            ConfirmTheManualSendingOfADisclaimerLetterPage(
                self.page
            ).click_confirm_button()
            SubjectScreeningSummaryPage(
                self.page
            ).click_record_return_of_disclaimer_letter()
            RecordInformedDissentPage(self.page).fill_notes_field(
                "AUTO TESTING: confirm not-immediate manual cease"
            )
            RecordInformedDissentPage(self.page).enter_date_confirmed(datetime.now())
            RecordInformedDissentPage(self.page).click_confirm_cease_button()


class ReasonForCeasing(Enum):
    INFORMED_DISSENT = ("Informed Dissent", 43, False)
    INFORMED_DISSENT_VERBAL_ONLY = ("Informed Dissent (verbal only)", 44, True)
    NO_COLON_SUBJECT_REQUEST = ("No Colon (subject request)", 45, False)
    NO_COLON_PROGRAMME_ASSESSED = ("No Colon (programme assessed)", 46, True)
    INFORMAL_DEATH = ("Informal Death", 47, True)

    def __init__(self, reason: str, value: int, is_immediate_cease_reason: bool):
        self._reason = reason
        self._value = value
        self._is_immediate_cease_reason = is_immediate_cease_reason

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def value(self) -> int:
        return self._value

    @property
    def is_immediate_cease(self) -> bool:
        return self._is_immediate_cease_reason

    @classmethod
    def by_description_case_insensitive(
        cls, reason: str
    ) -> Optional["ReasonForCeasing"]:
        """
        Get ReasonForCeasing member by description, case insensitive.
        Args:
            reason (str): The reason description to look for.
        Returns:
            Optional[ReasonForCeasing]: The matching ReasonForCeasing member, or None if not found.
        """
        reason_lower = reason.lower()
        for member in cls:
            if member.reason.lower() == reason_lower:
                return member
        return None
