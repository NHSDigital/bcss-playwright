from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from enum import StrEnum
import logging
import pytest
from utils.table_util import TableUtils


class SubjectEventsNotes(BasePage):
    """Subject Events Notes Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.table_utils = TableUtils(
            page, "#displayRS"
        )  # Initialize TableUtils for the table with id="displayRS"
        # Subject Events Notes - page filters
        self.additional_care_note_checkbox = self.page.get_by_label(
            "Additional Care Needs Note"
        )
        self.subject_note_checkbox = self.page.get_by_label("Subject Note")
        self.kit_note_checkbox = self.page.get_by_label("Kit Note")
        self.additional_care_note_type = self.page.locator("#UI_ADDITIONAL_CARE_NEED")
        self.notes_upto_500_char = self.page.get_by_label("Notes (up to 500 char)")
        self.update_notes_button = self.page.get_by_role("button", name="Update Notes")

    def select_additional_care_note(self) -> None:
        """Selects the 'Additional Care Needs Note' checkbox."""
        self.additional_care_note_checkbox.check()

    def select_additional_care_note_type(self, option: str) -> None:
        """Selects an option from the 'Additional Care Note Type' dropdown.

        Args:
            option (AdditionalCareNoteTypeOptions): The option to select from the dropdown.
                                                Use one of the predefined values from the
                                                AdditionalCareNoteTypeOptions enum, such as:
                                                - AdditionalCareNoteTypeOptions.LEARNING_DISABILITY
                                                - AdditionalCareNoteTypeOptions.SIGHT_DISABILITY
                                                - AdditionalCareNoteTypeOptions.HEARING_DISABILITY
                                                - AdditionalCareNoteTypeOptions.MOBILITY_DISABILITY
                                                - AdditionalCareNoteTypeOptions.MANUAL_DEXTERITY
                                                - AdditionalCareNoteTypeOptions.SPEECH_DISABILITY
                                                - AdditionalCareNoteTypeOptions.CONTINENCE_DISABILITY
                                                - AdditionalCareNoteTypeOptions.LANGUAGE
                                                - AdditionalCareNoteTypeOptions.OTHER
        """
        self.additional_care_note_type.select_option(option)

    def fill_notes(self, notes: str) -> None:
        """Fills the notes field with the provided text."""
        self.notes_upto_500_char.fill(notes)

    def dismiss_dialog_and_update_notes(self) -> None:
        """Clicks the 'Update Notes' button and handles the dialog by clicking 'OK'."""
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.update_notes_button.click()


class AdditionalCareNoteTypeOptions(StrEnum):
    """Enum for AdditionalCareNoteTypeOptions."""

    LEARNING_DISABILITY = "4120"
    SIGHT_DISABILITY = "4121"
    HEARING_DISABILITY = "4122"
    MOBILITY_DISABILITY = "4123"
    MANUAL_DEXTERITY = "4124"
    SPEECH_DISABILITY = "4125"
    CONTINENCE_DISABILITY = "4126"
    LANGUAGE = "4128"
    OTHER = "4127"
