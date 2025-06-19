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
        self.note_title = self.page.get_by_label("Note Title")
        self.additional_care_note_type = self.page.locator("#UI_ADDITIONAL_CARE_NEED")
        self.notes_upto_500_char = self.page.get_by_label("Notes (up to 500 char)")
        self.update_notes_button = self.page.get_by_role("button", name="Update Notes")
        self.note_type = self.page.locator("#UI_ADDITIONAL_CARE_NEED_FILTER")
        self.note_status = self.page.locator(
            "select[name^='UI_SUPPORTING_NOTE_STATUS_']"
        )

    def select_additional_care_note(self) -> None:
        """Selects the 'Additional Care Needs Note' checkbox."""
        self.additional_care_note_checkbox.check()

    def select_subject_note(self) -> None:
        """Selects the 'subject note' checkbox."""
        self.subject_note_checkbox.check()

    def select_kit_note(self) -> None:
        """Selects the 'kit note' checkbox."""
        self.kit_note_checkbox.check()

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

    def select_note_type(self, option: str) -> None:
        """
        Selects a note type from the dropdown menu.

        Args:
            option (str): The value of the option to select from the dropdown.
        """
        self.note_type.select_option(option)

    def select_note_status(self, option: str) -> None:
        """
        Selects a note status from the dropdown menu.

        Args:
            option (str): The value of the option to select from the dropdown.
        """
        self.note_status.select_option(option)

    def fill_note_title(self, title: str) -> None:
        """Fills the title field with the provided text."""
        self.note_title.fill(title)

    def fill_notes(self, notes: str) -> None:
        """Fills the notes field with the provided text."""
        self.notes_upto_500_char.fill(notes)

    def dismiss_dialog_and_update_notes(self) -> None:
        """Clicks the 'Update Notes' button and handles the dialog by clicking 'OK'."""
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.update_notes_button.click()

    def dismiss_dialog_and_add_replacement_note(self) -> None:
        """
        Dismisses the dialog and clicks the 'Add Replacement Note' button.
        """
        self.page.once("dialog", lambda dialog: dialog.dismiss())
        self.page.get_by_role("button", name="Add Replacement Note").click()

    def dismiss_dialog(self) -> None:
        """
        Dismisses a dialog when it appears.
        """
        self.page.once("dialog", lambda dialog: dialog.dismiss())

    def get_title_and_note_from_row(self, row_number: int = 0) -> dict:
        """
        Extracts title and note from a specific row's 'Notes' column using dynamic column index.
        """
        row_count = self.table_utils.get_row_count()
        if row_count == 0:
            raise ValueError("The table is empty.")

        # Find the 'Notes' column index (1-based)
        notes_col_index = self.table_utils.get_column_index("Notes")
        if notes_col_index == -1:
            raise ValueError("The 'Notes' column was not found in the table.")

        # Locate the cell at the specific row and column
        cell = self.page.locator(
            f"{self.table_utils} > tbody > tr:nth-child({row_number + 1}) > td:nth-child({notes_col_index})"
        )
        cell_text = cell.inner_text().strip()

        lines = cell_text.split("\n")
        title = lines[0].strip() if len(lines) > 0 else ""
        note = lines[1].strip() if len(lines) > 1 else ""

        return {"title": title, "note": note}


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


class NotesOptions(StrEnum):
    """Enum for NoteTypeOptions."""

    SUBJECT_NOTE = "4111"
    KIT_NOTE = "308015"
    ADDITIONAL_CARE_NOTE = "4112"


class NotesStatusOptions(StrEnum):
    """Enum for NoteStatusOptions."""

    ACTIVE = "4100"
    OBSOLETE = "4101"
    INVALID = "4102"
