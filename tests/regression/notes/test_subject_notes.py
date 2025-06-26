import logging
import pytest
from playwright.sync_api import Page, expect
from pages import screening_subject_search
from pages.logout.log_out_page import LogoutPage
from pages.base_page import BasePage
from pages.screening_subject_search import subject_screening_search_page
from pages.screening_subject_search import subject_screening_summary_page
from pages.screening_subject_search import subject_events_notes
from pages.screening_subject_search.subject_screening_search_page import (
    SubjectScreeningPage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.subject_events_notes import (
    NotesOptions,
    NotesStatusOptions,
    SubjectEventsNotes,
    AdditionalCareNoteTypeOptions,
)
from utils.user_tools import UserTools
from utils.table_util import TableUtils
from utils.oracle.oracle_specific_functions import (
    get_subjects_by_note_count,
    get_subjects_with_multiple_notes,
    get_supporting_notes,
)

def test_subject_does_not_have_a_subject_note(page: Page, general_properties: dict) -> None:
    """
    Test to check if I can identify if a subject does not have a Subject note
    """
    logging.info(
        f"Starting test: Verify subject does not have a '{general_properties["subject_note_name"]}'."
    )
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["subject_note_type_value"],
        general_properties["note_status_active"],
        0,
    )
    if subjects_df.empty:
        pytest.fail(
            f"No subjects found without '{general_properties["subject_note_name"]}'."
        )

    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify no subject notes are present
    logging.info(
        f"Verified that no '{general_properties['subject_note_name']}' link is visible for the subject."
    )
    # logging.info("Verifying that no additional care notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_note_link_not_present(
        general_properties["subject_note_name"]
    )

def test_add_a_subject_note_for_a_subject_without_a_note(
    page: Page, general_properties: dict) -> None:
    """
    Test to add a note for a subject without a subject note.
    """
    # User login
    logging.info(
        "Starting test: Add a '{general_properties['subject_note_name']}'  for a subject without a note."
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with no notes of the specified type
    subjects_df = get_subjects_by_note_count(
        general_properties["subject_note_type_value"],
        general_properties["note_status_active"],
        0,
    )
    if subjects_df.empty:
        pytest.fail(
            f"No subjects found for note type {general_properties["subject_note_type_value"]}."
        )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()

    # Navigate to Subject Events & Notes
    logging.info("Navigating to 'Subject Events & Notes' for the selected subject.")
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()

    # note type selection
    logging.info(
        f"Selecting note type based on value: '{general_properties["subject_note_type_value"]}'."
    )
    SubjectEventsNotes(page).select_subject_note()
    # Set the note status
    note_title = "Subject Note - General observation title"
    logging.info(f"Filling in notes: '{note_title}'.")
    SubjectEventsNotes(page).fill_note_title(note_title)
    # Set the note type for verification
    note_text = "Subject Note - General observation"
    logging.info(f"Filling in notes: '{note_text}'.")
    SubjectEventsNotes(page).fill_notes(note_text)
    # Dismiss dialog and update notes
    logging.info("Dismissing dialog and clicking 'Update Notes'.")
    SubjectEventsNotes(page).accept_dialog_and_update_notes()

    # Get supporting notes for the subject from DB
    logging.info(
        "Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(
        screening_subject_id, type_id, general_properties["note_status_active"]
    )
    logging.info(
        f"Retrieved notes for Screening Subject ID: {screening_subject_id}, Type ID: {type_id}."
    )
    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}."
    )
    assert (
        notes_df["title"].iloc[0].strip() == note_title
    ), f"Title does not match. Expected: '{note_title}', Found: '{notes_df['title'].iloc[0].strip()}'."
    assert (
        notes_df["note"].iloc[0].strip() == note_text
    ), f"Note does not match. Expected: '{note_text}', Found: '{notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: subject note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )
