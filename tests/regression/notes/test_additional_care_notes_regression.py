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


def test_subject_does_not_have_a_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status: int = 4100,
) -> None:
    """
    Test to check if I can identify if a subject does not have a Additional Care note
    """
    logging.info(f"Starting test: Verify subject does not have a '{note_type_name}'.")
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(note_type_value, note_status, 0)
    if subjects_df.empty:
        pytest.fail(f"No subjects found without '{note_type_name}'.")

    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify no additional care notes are present
    logging.info(
        "Verified that no'{note_type_name}'link is not visible for the subject."
    )
    # logging.info("Verifying that no additional care notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_note_link_not_present(note_type_name)


def test_add_an_additional_care_note_for_a_subject_without_a_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
) -> None:
    """
    Test to add a note for a subject without an existing note of a specified type .
    """
    # User login
    logging.info(
        "Starting test: Add a '{note_type_name}'  for a subject without a note."
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with no notes of the specified type
    subjects_df = get_subjects_by_note_count(note_type_value, note_status, 0)
    if subjects_df.empty:
        pytest.fail(f"No subjects found for note type {note_type_value}.")
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()

    # Navigate to Subject Events & Notes
    logging.info("Navigating to 'Subject Events & Notes' for the selected subject.")
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()

    # note type selection
    logging.info(f"Selecting note type based on value: '{note_type_value}'.")
    SubjectEventsNotes(page).select_additional_care_note()
    logging.info(f"Selecting Additional Care Note Type")
    note_title = "Additional Care Need - Learning disability"
    SubjectEventsNotes(page).select_additional_care_note_type(
        AdditionalCareNoteTypeOptions.LEARNING_DISABILITY
    )
    # Fill Notes
    note_text = "adding additional care need notes"
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
    notes_df = get_supporting_notes(screening_subject_id, type_id, note_status)
    # Filter the DataFrame to only include rows where type_id matches the current note_type_value
    filtered_notes_df = notes_df[notes_df["type_id"] == note_type_value]

    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}."
    )
    assert (
        filtered_notes_df["title"].iloc[0].strip() == note_title
    ), f"Title does not match. Expected: '{note_title}', Found: '{filtered_notes_df['title'].iloc[0].strip()}'."
    assert (
        filtered_notes_df["note"].iloc[0].strip() == note_text
    ), f"Note does not match. Expected: '{note_text}', Found: '{filtered_notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: Additional care note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )


def test_add_additional_care_note_for_subject_with_existing_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
) -> None:
    """
    Test to add an additional care note for a subject who already has an existing note.
    """
    # User login
    logging.info(
        "Starting test: Add an additional care note for a subject who already has additional care note."
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with existing additional care notes
    subjects_df = get_subjects_by_note_count(note_type_value, note_status, 1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Navigate to Subject Events & Notes
    logging.info("Navigating to 'Subject Events & Notes' for the selected subject.")
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()

    # add an Additional Care Note if the subject already has one
    logging.info("Selecting 'Additional Care Needs Note'.")
    SubjectEventsNotes(page).select_additional_care_note()

    # Select Additional Care Note Type
    note_title = "Additional Care Need - Learning disability"
    logging.info(f"Selecting Additional Care Note Type: '{note_title}'.")
    SubjectEventsNotes(page).select_additional_care_note_type(
        AdditionalCareNoteTypeOptions.LEARNING_DISABILITY
    )

    # Fill Notes
    note_text = "adding additional care need notes2"
    logging.info(f"Filling in notes: '{note_text}'.")
    SubjectEventsNotes(page).fill_notes(note_text)

    # Dismiss dialog and update notes
    logging.info("Dismissing dialog and clicking 'Update Notes'.")
    SubjectEventsNotes(page).accept_dialog_and_update_notes()
    # Get supporting notes for the subject
    logging.info(
        "Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    note_status = int(
        subjects_df["note_status"].iloc[0]
    )  # Get the note status from the DataFrame
    notes_df = get_supporting_notes(screening_subject_id, type_id, note_status)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == note_type_value]

    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}."
    )
    assert (
        filtered_notes_df["title"].iloc[0].strip() == note_title
    ), f"Title does not match. Expected: '{note_title}', Found: '{filtered_notes_df['title'].iloc[0].strip()}'."
    assert (
        filtered_notes_df["note"].iloc[0].strip() == note_text
    ), f"Note does not match. Expected: '{note_text}', Found: '{filtered_notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: Additional care note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )


def test_identify_subject_with_additional_care_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
) -> None:
    """
    Test to identify if a subject has an Additional Care note.
    """
    logging.info("Starting test: Verify subject has an additional care note.")
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(note_type_value, note_status, 1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has additional care notes  present
    logging.info("Verified: Aadditional care notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_additional_care_note_visible()


def test_view_active_additional_care_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
) -> None:
    """
    Test to verify if an active Additional Care note is visible for a subject.
    """
    logging.info("Starting test: Verify subject has an additional care note.")
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(note_type_value, 1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has additional care notes  present
    logging.info("Verified: Aadditional care notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    logging.info(
        f"Verifying that the Additional Care Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_additional_care_note_visible()
    logging.info(
        f"Clicking on the 'Additional Care Note' link for the subject with NHS Number: {nhs_no}."
    )

    SubjectScreeningSummaryPage(page).click_subjects_events_notes()
    SubjectEventsNotes(page).select_note_type(NotesOptions.ADDITIONAL_CARE_NOTE)

    # Get supporting notes for the subject
    logging.info(
        "Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(screening_subject_id, type_id, note_status)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == note_type_value]
    # Get the title and note from the first row of the UI table
    ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(2)
    logging.info(f"Data from UI: {ui_data}")

    # Get the title and note from the database
    db_data = {
        "title": filtered_notes_df["title"].iloc[0].strip(),
        "note": filtered_notes_df["note"].iloc[0].strip(),
    }
    logging.info(f"Data from DB: {db_data}")

    # Compare the data
    assert (
        ui_data["title"] == db_data["title"]
    ), f"Title does not match. UI: '{ui_data['title']}', DB: '{db_data['title']}'"
    assert (
        ui_data["note"] == db_data["note"]
    ), f"Note does not match. UI: '{ui_data['note']}', DB: '{db_data['note']}'"


def test_update_existing_additional_care_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
) -> None:
    """
    Test to verify if an existing Additional Care note can be updated successfully.
    """
    logging.info("Starting test: Verify subject has an additional care note.")
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    # user login
    logging.info("Logging in as 'ScreeningAssistant at BCS02'.")
    UserTools.user_login(page, "ScreeningAssistant at BCS02")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(note_type_value, note_status, 1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has additional care notes  present
    logging.info("Verified: Additional care notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    logging.info(
        f"Verifying that the Additional Care Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_additional_care_note_visible()
    logging.info(
        f"Clicking on the 'Additional Care Note' link for the subject with NHS Number: {nhs_no}."
    )

    SubjectScreeningSummaryPage(page).click_subjects_events_notes()
    SubjectEventsNotes(page).select_note_type(NotesOptions.ADDITIONAL_CARE_NOTE)
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).note_status, NotesStatusOptions.INVALID
    )
    SubjectEventsNotes(page).select_additional_care_note()
    SubjectEventsNotes(page).select_additional_care_note_type(
        AdditionalCareNoteTypeOptions.HEARING_DISABILITY
    )
    SubjectEventsNotes(page).fill_notes("updated additional care note")
    SubjectEventsNotes(page).accept_dialog_and_add_replacement_note()

    # Get updated supporting notes for the subject
    logging.info(
        "Retrieving updated supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    note_status = int(
        subjects_df["note_status"].iloc[0]
    )  # Get the note status from the DataFrame
    notes_df = get_supporting_notes(screening_subject_id, type_id, note_status)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == note_type_value]
    # Verify title and note match the provided values
    logging.info("Verifying that the updated title and note match the provided values.")

    # Define the expected title and note
    note_title = "Additional Care Need - Hearing disability"
    note_text = "updated additional care note"

    # Ensure the filtered DataFrame is not empty
    if filtered_notes_df.empty:
        pytest.fail(
            f"No notes found for type_id: {type_id}. Expected at least one updated note."
        )

    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}."
    )
    assert (
        filtered_notes_df["title"].iloc[0].strip() == note_title
    ), f"Title does not match. Expected: '{note_title}', Found: '{filtered_notes_df['title'].iloc[0].strip()}'."
    assert (
        filtered_notes_df["note"].iloc[0].strip() == note_text
    ), f"Note does not match. Expected: '{note_text}', Found: '{filtered_notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: Additional care note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_title}', Note: '{note_text}'."
    )


def test_remove_existing_additional_care_note(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
) -> None:
    """
    Test to verify if an existing Additional Care note can be removed for a subject with one Additional Care note.
    """
    logging.info(
        "Starting test: Verify if an existing Additional Care note can be removed for a subject with one Additional Care note"
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    # user login
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Search for the subject by NHS Number.")
    subjects_df = get_subjects_by_note_count(note_type_value, note_status, 1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has additional care notes  present
    logging.info("Verified: Aadditional care notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    logging.info(
        f"Verifying that the Additional Care Note is visible for the subject with NHS Number: {nhs_no}."
    )
    SubjectScreeningSummaryPage(page).verify_additional_care_note_visible()
    logging.info(
        f"Clicking on the 'Additional Care Note' link for the subject with NHS Number: {nhs_no}."
    )

    SubjectScreeningSummaryPage(page).click_subjects_events_notes()
    SubjectEventsNotes(page).select_note_type(NotesOptions.ADDITIONAL_CARE_NOTE)
    logging.info(
        "Selecting the 'Obsolete' option for the existing Additional Care Note."
    )
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).note_status, NotesStatusOptions.OBSOLETE
    )
    logging.info("Verifying that the subject does not have any Additional Care Notes.")

    # Retrieve the Screening Subject ID
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    # type_id = 4112  # Type ID for Additional Care Notes
    # note_status = 4100  # Status ID for Active Notes
    notes_df = get_supporting_notes(screening_subject_id, type_id, note_status)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == note_type_value]
    # Verify that the filtered DataFrame is empty
    if not filtered_notes_df.empty:
        pytest.fail(
            f"Subject has Additional Care Notes. Expected none, but found: {filtered_notes_df}"
        )

    logging.info(
        "Verification successful: Subject does not have any active Additional Care Notes."
    )


def test_remove_existing_additional_care_note_for_subject_with_multiple_notes(
    page: Page,
    note_type_name: str = "Additional Care Note",
    note_type_value: int = 4112,
    note_status=4100,
    note_status_obsolete=4101,
) -> None:
    """
    Test to verify if an existing Additional Care note can be removed for a subject with multiple Additional Care notes.
    """
    # User login
    logging.info(
        "Starting test: Remove an additional care note for a subject who already has multiple additional care note."
    )
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with multiple additional care notes
    subjects_df = get_subjects_with_multiple_notes(note_type_value)
    if subjects_df.empty:
        logging.info(
            "No subjects found with multiple Additional Care Notes. Skipping test."
        )
        pytest.fail("No subjects found with multiple Additional Care Notes.")
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Navigate to Subject Events & Notes
    logging.info("Navigating to 'Subject Events & Notes' for the selected subject.")
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()

    SubjectEventsNotes(page).select_note_type(NotesOptions.ADDITIONAL_CARE_NOTE)
    # Select the first Additional Care Note from the table for removal
    logging.info("Selecting the first Additional Care Note from the table for removal.")
    ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(2)
    logging.info(
        "Removing one of the existing Additional Care Note by selecting 'Obsolete' option "
    )
    BasePage(page).safe_accept_dialog_select_option(
        SubjectEventsNotes(page).note_status, NotesStatusOptions.OBSOLETE
    )
    logging.info(
        "Verifying that the subject's removed additional care note is removed from DB as well "
    )

    # Retrieve the Screening Subject ID
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")

    # Get the notes from the database
    notes_df = get_supporting_notes(screening_subject_id, note_type_value, note_status)
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
        screening_subject_id, note_type_value, note_status_obsolete
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
