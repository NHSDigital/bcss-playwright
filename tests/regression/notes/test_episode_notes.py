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


def test_subject_does_not_have_a_episode_note(
    page: Page, general_properties: dict
) -> None:
    """
    Test to check if I can identify if a subject does not have a episode note
    """
    logging.info(
        f"Starting test: Verify subject does not have a '{general_properties["episode_note_name"]}'."
    )
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["episode_note_type_value"],
        general_properties["note_status_active"],
        0,
    )
    if subjects_df.empty:
        pytest.fail(
            f"No subjects found without '{general_properties["episode_note_name"]}'."
        )

    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify no episode notes are present
    logging.info(
        f"Verified that no '{general_properties['episode_note_name']}' link is visible for the subject."
    )
    # logging.info("Verifying that no episode notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_note_link_not_present(
        general_properties["episode_note_name"]
    )


def test_add_a_episode_note_for_a_subject_without_a_note(
    page: Page, general_properties: dict
) -> None:
    """
    Test to add a episode note for a subject without a episode note.
    """
    # User login
    logging.info(
        "Starting test: Add a '{general_properties['episode_note_name']}'  for a subject without a note."
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with no notes of the specified type
    subjects_df = get_subjects_by_note_count(
        general_properties["episode_note_type_value"],
        general_properties["note_status_active"],
        0,
    )
    if subjects_df.empty:
        pytest.fail(
            f"No subjects found for note type {general_properties["episode_note_type_value"]}."
        )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Click on the Episode link
    SubjectScreeningSummaryPage(page).click_list_episodes()
    logging.info("Clicked on the list Episode link.")

    # Select the first link from the table
    TableUtils(page, "#displayRS").click_first_link_in_column("View Events")
    logging.info("Selected the first events link from the table.")

    note_title = "Episode Note - Follow-up required title"
    # Set the note type for verification
    note_text = "Episode Note - Follow-up required"
    SubjectEventsNotes(page).fill_note_title(note_title)
    # Set the note type for verification
    logging.info(f"Filling in notes: '{note_text}'.")
    SubjectEventsNotes(page).fill_notes(note_text)
    # Dismiss dialog and update notes
    logging.info("Accepting dialog and clicking 'Update Notes'.")
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
        f"Verification successful: episode note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )

def test_identify_subject_with_episode_note(
    page: Page, general_properties: dict
) -> None:
    """
    Test to identify if a subject has a episode note.
    """
    logging.info("Starting test: Verify subject has a episode note.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["episode_note_type_value"],
        general_properties["note_status_active"],
        1,
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has episode notes  present
    logging.info("Verified: episode notes are present for the subject.")
    # logging.info("Verifying that  episode notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["episode_note_name"]
    )


def test_view_active_episode_note(page: Page, general_properties: dict) -> None:
    """
    Test to verify if an active episode note is visible for a subject.
    """
    logging.info("Starting test: Verify subject has episode  note.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["episode_note_type_value"], 1
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has episode notes  present
    logging.info("Verified: episode notes are present for the subject.")
    # logging.info("Verifying that  episode notes are present for the subject.")
    logging.info(
        f"Verifying that the episode Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["episode_note_name"]
    )

    SubjectScreeningSummaryPage(page).click_list_episodes()
    # Select the first link from the table
    TableUtils(page, "#displayRS").click_first_link_in_column("View Events")
    logging.info("Selected the first events link from the table.")
    SubjectEventsNotes(page).select_note_type(NotesOptions.EPISODE_NOTE)

    # Get supporting notes for the subject
    logging.info(
        "Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(
        screening_subject_id, type_id, general_properties["note_status_active"]
    )
    # Get the title and note from the first row of the UI table
    ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(2)
    logging.info(f"Data from UI: {ui_data}")

    # Get the title and note from the database
    db_data = {
        "title": notes_df["title"].iloc[0].strip(),
        "note": notes_df["note"].iloc[0].strip(),
    }
    logging.info(f"Data from DB: {db_data}")

    # Compare the data
    assert (
        ui_data["title"] == db_data["title"]
    ), f"Title does not match. UI: '{ui_data['title']}', DB: '{db_data['title']}'"
    assert (
        ui_data["note"] == db_data["note"]
    ), f"Note does not match. UI: '{ui_data['note']}', DB: '{db_data['note']}'"


def test_update_existing_episode_note(page: Page, general_properties: dict) -> None:
    """
    Test to verify if an existing episode note can be updated successfully.
    """
    logging.info("Starting test: Verify subject has a episode note.")
    # user login
    logging.info("Logging in as 'TeamLeader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()
    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["episode_note_type_value"],
        general_properties["note_status_active"],
        1,
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has episode notes  present
    logging.info(
        f"Verifying that the subject Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["episode_note_name"]
    )
    SubjectScreeningSummaryPage(page).click_list_episodes()
    # Select the first link from the table
    TableUtils(page, "#displayRS").click_first_link_in_column("View Events")
    logging.info("Selected the first events link from the table.")
    SubjectEventsNotes(page).select_note_type(NotesOptions.EPISODE_NOTE)
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).episode_note_status, NotesStatusOptions.INVALID
    )
    SubjectEventsNotes(page).fill_note_title("updated episode title")
    SubjectEventsNotes(page).fill_notes("updated episode note")
    SubjectEventsNotes(page).accept_dialog_and_add_replacement_note()

    # Get updated supporting notes for the subject
    logging.info(
        "Retrieving updated supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(
        screening_subject_id, type_id, general_properties["note_status_active"]
    )
    # Verify title and note match the provided values
    logging.info("Verifying that the updated title and note match the provided values.")

    # Define the expected title and note
    note_title = "updated episode title"
    note_text = "updated episode note"

    # Ensure the filtered DataFrame is not empty
    if notes_df.empty:
        pytest.fail(
            f"No notes found for type_id: {general_properties["episode_note_type_value"]}. Expected at least one updated note."
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
        f"Verification successful:Episode note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )
