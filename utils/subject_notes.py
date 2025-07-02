import logging
import pytest
from playwright.sync_api import Page
import pandas as pd
from typing import Optional
from pages import login
from pages.base_page import BasePage
from pages.screening_subject_search.subject_screening_search_page import (
    SubjectScreeningPage,
)
from pages.screening_subject_search.subject_events_notes import (
    NotesOptions,
    NotesStatusOptions,
    SubjectEventsNotes,
    AdditionalCareNoteTypeOptions,
)
from utils.oracle.oracle_specific_functions import (
    get_subjects_by_note_count,
    get_subjects_with_multiple_notes,
    get_supporting_notes,
)


# search for a subject by NHS number and area option
def search_subject_by_nhs(page: Page, nhs_no: str, area_option: str = "07") -> None:
    """
    Searches for a subject using their NHS number and a specified area option.

    :param page: The Page object for browser interaction
    :param nhs_no: NHS number of the subject to search for
    :param area_option: Search area option (default is "07")
    """
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option(area_option)
    SubjectScreeningPage(page).click_search_button()


# Get Supporting notes from DB
def fetch_supporting_notes_from_db(
    subjects_df: pd.DataFrame, nhs_no: str, note_status: str
) -> tuple[int, int, pd.DataFrame]:
    """
    Retrieves supporting notes from the database using subject and note info.

    :param subjects_df: DataFrame containing subject information
    :param nhs_no: NHS Number of the subject
    :param note_status: Status of the note (e.g., active)
    :return: Tuple of (screening_subject_id, type_id, notes_df)
    """
    logging.info(
        f"Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")

    type_id = int(subjects_df["type_id"].iloc[0])

    notes_df = get_supporting_notes(screening_subject_id, type_id, int(note_status))
    logging.info(
        f"Retrieved notes for Screening Subject ID: {screening_subject_id}, Type ID: {type_id}."
    )

    return screening_subject_id, type_id, notes_df


def verify_note_content_matches_expected(
    notes_df: pd.DataFrame,
    expected_title: str,
    expected_note: str,
    type_id: int,
) -> None:
    """
    Verifies that the title and note fields from the DataFrame match the expected values.

    :param notes_df: DataFrame containing the actual note data.
    :param expected_title: Expected note title.
    :param expected_note: Expected note content.
    :param nhs_no: NHS Number of the subject (for logging).
    :param type_id: Note type ID (for logging).
    """
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}."
    )

    actual_title = notes_df["title"].iloc[0].strip()
    actual_note = notes_df["note"].iloc[0].strip()

    assert actual_title == expected_title, (
        f"Title does not match. Expected: '{expected_title}', "
        f"Found: '{actual_title}'."
    )
    assert (
        actual_note == expected_note
    ), f"Note does not match. Expected: '{expected_note}', Found: '{actual_note}'."


def verify_note_content_ui_vs_db(
    page: Page,
    notes_df: pd.DataFrame,
    row_index: int = 2,
    title_prefix_to_strip: Optional[str] = None,
) -> None:
    """
    Verifies that the note title and content from the UI match the database values.

    :param page: The page object to interact with UI
    :param notes_df: DataFrame containing note data from DB
    :param row_index: The row index in the UI table to fetch data from (default is 2)
    :param title_prefix_to_strip: Optional prefix to remove from UI title (e.g., "Subject Kit Note -")
    """
    ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(row_index)
    logging.info(f"Data from UI: {ui_data}")

    if title_prefix_to_strip:
        ui_data["title"] = ui_data["title"].replace(title_prefix_to_strip, "").strip()
        logging.info(f"Data from UI after title normalization: {ui_data}")

    db_data = {
        "title": notes_df["title"].iloc[0].strip(),
        "note": notes_df["note"].iloc[0].strip(),
    }
    logging.info(f"Data from DB: {db_data}")

    assert (
        ui_data["title"] == db_data["title"]
    ), f"Title does not match. UI: '{ui_data['title']}', DB: '{db_data['title']}'"

    assert (
        ui_data["note"] == db_data["note"]
    ), f"Note does not match. UI: '{ui_data['note']}', DB: '{db_data['note']}'"


def verify_note_removal_and_obsolete_transition(
    subjects_df: pd.DataFrame,
    ui_data: dict,
    general_properties: dict,
    note_type_key: str,
    status_active_key: str,
    status_obsolete_key: str,
) -> None:
    """
    Verifies that a note was removed from active notes and appears in obsolete notes.

    :param subjects_df: DataFrame with subject details
    :param ui_data: Dict with 'title' and 'note' from UI
    :param general_properties: Dictionary with environment settings
    :param note_type_key: Key to access the note type from general_properties
    :param status_active_key: Key for active status
    :param status_obsolete_key: Key for obsolete status
    """
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")

    note_type = general_properties[note_type_key]
    note_status_active = general_properties[status_active_key]
    note_status_obsolete = general_properties[status_obsolete_key]

    removed_title = ui_data["title"].strip()
    removed_note = ui_data["note"].strip()

    # Check active notes
    active_notes_df = get_supporting_notes(
        screening_subject_id, note_type, note_status_active
    )
    logging.info("Checking active notes for removed note presence.")
    for _, row in active_notes_df.iterrows():
        db_title = row["title"].strip()
        db_note = row["note"].strip()
        logging.info(f"Active note: Title='{db_title}', Note='{db_note}'")
        assert (
            db_title != removed_title or db_note != removed_note
        ), f"❌ Removed note still present in active notes. Title: '{db_title}', Note: '{db_note}'"

    logging.info("✅ Removed note is not present in active notes.")

    # Check obsolete notes
    obsolete_notes_df = get_supporting_notes(
        screening_subject_id, note_type, note_status_obsolete
    )
    logging.info("Verifying presence of removed note in obsolete notes.")

    found = any(
        row["title"].strip() == removed_title and row["note"].strip() == removed_note
        for _, row in obsolete_notes_df.iterrows()
    )

    assert (
        found
    ), f"❌ Removed note NOT found in obsolete list. Title: '{removed_title}', Note: '{removed_note}'"
    logging.info("✅ Removed note confirmed in obsolete notes.")
