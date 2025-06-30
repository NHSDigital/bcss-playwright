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


@pytest.mark.regression
@pytest.mark.note_tests
def test_subject_does_not_have_a_subject_note(
    page: Page, general_properties: dict
) -> None:
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


@pytest.mark.regression
@pytest.mark.note_tests
def test_add_a_subject_note_for_a_subject_without_a_note(
    page: Page, general_properties: dict
) -> None:
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


@pytest.mark.regression
@pytest.mark.note_tests
def test_identify_subject_with_subject_note(
    page: Page, general_properties: dict
) -> None:
    """
    Test to identify if a subject has an subject note.
    """
    logging.info("Starting test: Verify subject has a subject note.")
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
        1,
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has subject notes  present
    logging.info("Verified: Subject notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["subject_note_name"]
    )


@pytest.mark.regression
@pytest.mark.note_tests
def test_view_active_subject_note(page: Page, general_properties: dict) -> None:
    """
    Test to verify if an active subject note is visible for a subject.
    """
    logging.info("Starting test: Verify subject has subject  note.")
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["subject_note_type_value"], 1
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has subject notes  present
    logging.info("Verified: subject notes are present for the subject.")
    # logging.info("Verifying that  subject notes are present for the subject.")
    logging.info(
        f"Verifying that the subject Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["subject_note_name"]
    )

    SubjectScreeningSummaryPage(page).click_subjects_events_notes()
    SubjectEventsNotes(page).select_note_type(NotesOptions.SUBJECT_NOTE)

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


@pytest.mark.regression
@pytest.mark.note_tests
def test_update_existing_subject_note(page: Page, general_properties: dict) -> None:
    """
    Test to verify if an existing subject note can be updated successfully.
    """
    logging.info("Starting test: Verify subject has a subject note.")
    # user login
    logging.info("Logging in as 'TeamLeader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()
    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["subject_note_type_value"],
        general_properties["note_status_active"],
        1,
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has subject notes  present
    logging.info(
        f"Verifying that the subject Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["subject_note_name"]
    )
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()
    SubjectEventsNotes(page).select_note_type(NotesOptions.SUBJECT_NOTE)
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).note_status, NotesStatusOptions.INVALID
    )
    SubjectEventsNotes(page).fill_note_title("updated subject title")
    SubjectEventsNotes(page).fill_notes("updated subject note")
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
    note_title = "updated subject title"
    note_text = "updated subject note"

    # Ensure the filtered DataFrame is not empty
    if notes_df.empty:
        pytest.fail(
            f"No notes found for type_id: {general_properties["subject_note_type_value"]}. Expected at least one updated note."
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
        f"Verification successful:Subject note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )


@pytest.mark.regression
@pytest.mark.note_tests
def test_remove_existing_subject_note(page: Page, general_properties: dict) -> None:
    """
    Test to verify if an existing Subject note can be removed for a subject with one Subject note.
    """
    logging.info(
        "Starting test: Verify if an existing Subject note can be removed for a subject with one Subject note"
    )
    # user login
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(
        general_properties["subject_note_type_value"],
        general_properties["note_status_active"],
        1,
    )
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has subject notes  present
    logging.info(
        f"Verifying that the Subject Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_note_link_present(
        general_properties["subject_note_name"]
    )
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()
    SubjectEventsNotes(page).select_note_type(NotesOptions.SUBJECT_NOTE)
    logging.info("Selecting the 'Obsolete' option for the existing Subject Note.")
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).note_status, NotesStatusOptions.OBSOLETE
    )
    logging.info("Verifying that the subject does not have any Subject Notes.")

    # Retrieve the Screening Subject ID
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(
        screening_subject_id, type_id, general_properties["note_status_active"]
    )
    # Verify that the DataFrame is not empty
    if not notes_df.empty:
        pytest.fail(f"Subject has Subject Notes. Expected none, but found: {notes_df}")

    logging.info(
        "Verification successful: Subject does not have any active Subject Notes."
    )


@pytest.mark.regression
@pytest.mark.note_tests
def test_remove_existing_subject_note_for_subject_with_multiple_notes(
    page: Page, general_properties: dict
) -> None:
    """
    Test to verify if an existing subject note can be removed for a subject with multiple Subject notes.
    """
    # User login
    logging.info(
        "Starting test: Remove a subject note for a subject who already has multiple Subject note."
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with multiple subject notes
    subjects_df = get_subjects_with_multiple_notes(
        general_properties["subject_note_type_value"]
    )
    if subjects_df.empty:
        logging.info("No subjects found with multiple Subject Notes.")
        pytest.fail("No subjects found with multiple Subject Notes.")
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Navigate to Subject Events & Notes
    logging.info("Navigating to 'Subject Events & Notes' for the selected subject.")
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()

    SubjectEventsNotes(page).select_note_type(NotesOptions.SUBJECT_NOTE)
    # Select the first Subject Note from the table for removal
    logging.info("Selecting the first Subject Note from the table for removal.")
    ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(2)
    logging.info(
        "Removing one of the existing Subject Note by selecting 'Obsolete' option "
    )
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).note_status, NotesStatusOptions.OBSOLETE
    )
    logging.info(
        "Verifying that the subject's removed subject note is removed from DB as well "
    )

    # Retrieve the Screening Subject ID
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")

    # Get the notes from the database
    notes_df = get_supporting_notes(
        screening_subject_id,
        general_properties["subject_note_type_value"],
        general_properties["note_status_active"],
    )
    # Loop through the list of active notes and check if the removed note is still present
    logging.info(
        "Looping through active notes to verify the removed note is not present."
    )
    removed_note_title = ui_data["title"].strip()
    removed_note_text = ui_data["note"].strip()
    for index, row in notes_df.iterrows():
        # Get the title and note from the database
        db_title = row["title"].strip()
        db_note = row["note"].strip()

        logging.info(f"Checking note: Title='{db_title}', Note='{db_note}'")

        # Assert that the removed note is not present among active notes
        assert (
            db_title != removed_note_title or db_note != removed_note_text
        ), f"Removed note is still present in active notes. Title: '{db_title}', Note: '{db_note}'"

        logging.info(
            "Verification successful: Removed note is not present among active notes."
        )
    # query to retrieving obsolete notes of the same type for the subject.
    logging.info("Retrieving obsolete notes of the same type for the subject.")

    # Get the notes from the database
    notes_df = get_supporting_notes(
        screening_subject_id,
        general_properties["subject_note_type_value"],
        general_properties["note_status_obsolete"],
    )
    # Verify that the removed note is present among obsolete notes
    logging.info("Verifying that the removed note is present among obsolete notes.")
    logging.info(
        f"Removed Note Title: '{removed_note_title}', Removed Note Text: '{removed_note_text}'"
    )

    # Flag to track if the removed note is found
    found = False

    # Loop through the list of obsolete notes
    for index, row in notes_df.iterrows():
        # Get the title and note from the database
        db_title = row["title"].strip()
        db_note = row["note"].strip()

        logging.info(f"Checking obsolete note: Title='{db_title}', Note='{db_note}'")

        # Check if the removed note matches any obsolete note
        if db_title == removed_note_title and db_note == removed_note_text:
            found = True
        break

    # Assert that the removed note is found in the obsolete list
    assert (
        found
    ), f"Removed note is not present in the obsolete list. Title: '{removed_note_title}', Note: '{removed_note_text}'"

    logging.info(
        "Verification successful: Removed note is present in the obsolete list."
    )
