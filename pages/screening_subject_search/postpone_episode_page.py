from playwright.sync_api import Page
from pages.base_page import BasePage
from datetime import datetime
from utils.calendar_picker import CalendarPicker


class PostponeEpisodePage(BasePage):
    """Postpone Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Postpone Episode page - page locators
        self.reason_dropwdown = self.page.locator("#CLOSE_REASON")
        self.clinical_reason_dropwdown = self.page.locator(
            "#UI_CLINICAL_REASON_FOR_CLOSURE"
        )
        self.notes_field = self.page.locator("#UI_NOTES_TEXT")
        self.reason_for_date_change_dropdown = self.page.locator(
            "#A_C_SSDDReasonForChange"
        )
        self.postpone_episode_button = self.page.get_by_role(
            "button", name="Postpone Episode"
        )

    def select_reason_dropdown_option(self, option: str) -> None:
        """
        This method is designed to select an option from the Reason dropdown.
        Args:
            option (str): The option to select from the dropdown.
        """
        self.reason_dropwdown.select_option(label=option)

    def select_clinical_reason_dropdown_option(self, option: str) -> None:
        """
        This method is designed to select an option from the Clinical Reason dropdown.
        Args:
            option (str): The option to select from the dropdown.
        """
        self.clinical_reason_dropwdown.select_option(label=option)

    def enter_notes(self, notes: str) -> None:
        """
        Enters notes in the Notes field.
        Args:
            notes (str): The notes to enter in the field.
        """
        self.notes_field.fill(notes)

    def select_reason_for_date_change_dropdown_option(self, option: str) -> None:
        """
        This method is designed to select an option from the Reason for Date Change dropdown.
        Args:
            option (str): The option to select from the dropdown.
        """
        self.reason_for_date_change_dropdown.select_option(label=option)

    def click_postpone_episode_button(self) -> None:
        """Clicks the Postpone Episode button."""
        self.safe_accept_dialog(self.postpone_episode_button)
