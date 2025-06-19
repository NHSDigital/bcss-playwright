from ast import Sub
import logging
from re import A
import pytest
from playwright.sync_api import Page, expect
from sqlalchemy import Table
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
    get_supporting_notes,
)


def note_types_order():
    return [
        ("Additional Care Note", 4112),
        ("Episode Note", 4110),
        ("Subject Note", 4111),
        ("Kit Note", 308015),
    ]


@pytest.mark.parametrize("note_type_name, note_type_value", note_types_order())
def test_subject_does_not_have_a_note(
    page: Page, note_type_name: str, note_type_value: int
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
    subjects_df = get_subjects_by_note_count(note_type_value, 0)
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


@pytest.mark.parametrize("note_type_name, note_type_value", note_types_order())
def test_add_an_additional_care_note_for_a_subject_without_a_note(
    page: Page, note_type_name: str, note_type_value: int
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
    subjects_df = get_subjects_by_note_count(note_type_value, 0)
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

    # Dynamically handle note type selection
    logging.info(f"Selecting note type based on value: '{note_type_value}'.")

    if note_type_value == 4110:  # Episode Note
        # Specific path for Episode Note
        logging.info("Navigating to the Episode Note path.")

        # Click on the Episode link
        SubjectScreeningSummaryPage(page).click_list_episodes()
        logging.info("Clicked on the list Episode link.")

        # Select the first link from the table
        TableUtils(page, "#displayRS").click_first_link_in_column("View Events")
        logging.info("Selected the first events link from the table.")

        # Select the radio button for Episode Note
        # SubjectEventsNotes(page).select_episode_note_radio_button()
        logging.info("Selected the radio button for Episode Note.")
        note_title = "Episode Note - Follow-up required title"
        # Set the note type for verification
        note_type = "Episode Note - Follow-up required"

    elif note_type_value == 4112:  # Additional Care Note
        # Select Additional Care Note
        logging.info("Selecting 'Additional Care Note'.")
        SubjectEventsNotes(page).select_additional_care_note()

        # Select Additional Care Note Type
        note_type = "Additional Care Need - Learning disability"
        logging.info(f"Selecting Additional Care Note Type: '{note_type}'.")
        SubjectEventsNotes(page).select_additional_care_note_type(
            AdditionalCareNoteTypeOptions.LEARNING_DISABILITY
        )

    elif note_type_value == 4111:  # Subject Note
        # Select Subject Note
        logging.info("Selecting 'Subject Note'.")
        SubjectEventsNotes(page).select_subject_note()
        note_title = "Subject Note - General observation title"
        # Set the note type for verification
        note_type = "Subject Note - General observation"

    elif note_type_value == 308015:  # Kit Note
        # Select Kit Note
        logging.info("Selecting 'Kit Note'.")
        SubjectEventsNotes(page).select_kit_note()
        note_title = "Kit Note - Equipment issue title"
        # Set the note type for verification
        note_type = "Kit Note - Equipment issue"
    else:
        pytest.fail(f"Unsupported note type value: {note_type_value}")
    # Fill title and Notes

    if note_type_value == 4112:  # Additional Care Note
        # Only fill the note text for Additional Care Note
        note_text = f"Adding a note for type '{note_type_value}'."
        logging.info(f"Filling in notes: '{note_text}'.")
        SubjectEventsNotes(page).fill_notes(note_text)
    else:
        # Fill both title and note text for other note types
        note_text = f"Adding a note for type '{note_type_value}'."
        logging.info(f"Filling in title: '{note_title}' and notes: '{note_text}'.")
        SubjectEventsNotes(page).fill_note_title(note_title)
        SubjectEventsNotes(page).fill_notes(note_text)

    # Dismiss dialog and update notes
    logging.info("Dismissing dialog and clicking 'Update Notes'.")
    SubjectEventsNotes(page).dismiss_dialog_and_update_notes()

    # Navigate back
    logging.info("Navigating back to the Subject Screening Summary Page.")
    BasePage(page).click_back_button()

    # Get supporting notes for the subject
    logging.info(
        "Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(screening_subject_id, type_id)
    # Filter the DataFrame to only include rows where type_id matches the current note_type_value
    filtered_notes_df = notes_df[notes_df["type_id"] == note_type_value]

    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id:{note_type_value}."
    )
    # Dynamically set the expected title
    if note_type_value == 4112:  # Additional Care Note
        expected_title = (
            note_type  # Title is automatically set based on the selected type
        )
    else:
        expected_title = note_title  # Use the title explicitly passed to the UI

    # Verify title and note match the provided values
    assert (
        filtered_notes_df["title"].iloc[0].strip() == expected_title
    ), f"Title does not match. Expected: '{expected_title}', Found: '{filtered_notes_df['title'].iloc[0].strip()}'."
    assert (
        filtered_notes_df["note"].iloc[0].strip() == note_text
    ), f"Note does not match. Expected: '{note_text}', Found: '{filtered_notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: Note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{expected_title}', Note: '{note_text}'."
    )


def test_add_additional_care_note_for_subject_with_existing_note(
    page: Page,
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
    subjects_df = get_subjects_by_note_count(4112, 1)
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
    note_type = "Additional Care Need - Learning disability"
    logging.info(f"Selecting Additional Care Note Type: '{note_type}'.")
    SubjectEventsNotes(page).select_additional_care_note_type(
        AdditionalCareNoteTypeOptions.LEARNING_DISABILITY
    )

    # Fill Notes
    note_text = "adding additional care need notes2"
    logging.info(f"Filling in notes: '{note_text}'.")
    SubjectEventsNotes(page).fill_notes(note_text)

    # Dismiss dialog and update notes
    logging.info("Dismissing dialog and clicking 'Update Notes'.")
    SubjectEventsNotes(page).dismiss_dialog_and_update_notes()
    # Get supporting notes for the subject
    logging.info(
        "Retrieving supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(screening_subject_id, type_id)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == type_id]

    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}."
    )
    assert (
        filtered_notes_df["title"].iloc[0].strip() == note_type
    ), f"Title does not match. Expected: '{note_type}', Found: '{filtered_notes_df['title'].iloc[0].strip()}'."
    assert (
        filtered_notes_df["note"].iloc[0].strip() == note_text
    ), f"Note does not match. Expected: '{note_text}', Found: '{filtered_notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: Additional care note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_type}', Note: '{note_text}'."
    )


def test_identify_subject_with_additional_care_note(page: Page) -> None:
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
    subjects_df = get_subjects_by_note_count(4112, 1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has additional care notes  present
    logging.info("Verified: Aadditional care notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_additional_care_note_visible()


@pytest.mark.wip
def test_view_active_additional_care_note(page: Page) -> None:
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
    subjects_df = get_subjects_by_note_count(4112, 1)
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
    notes_df = get_supporting_notes(screening_subject_id, type_id)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == type_id]
    # Get the title and note from the first row of the UI table
    ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(
        0
    )  # Row 0 is the first row
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


def test_update_existing_additional_care_note(page: Page) -> None:
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
    subjects_df = get_subjects_by_note_count(4112, 1)
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
    # page.locator("#UI_ADDITIONAL_CARE_NEED_FILTER").select_option("4112")
    SubjectEventsNotes(page).select_note_status(NotesStatusOptions.INVALID)
    # page.locator("#UI_SUPPORTING_NOTE_STATUS_10623").select_option("4102")
    SubjectEventsNotes(page).dismiss_dialog()
    SubjectEventsNotes(page).select_additional_care_note()
    # page.get_by_label("Note Title").select_option("4102")
    SubjectEventsNotes(page).select_additional_care_note_type(
        AdditionalCareNoteTypeOptions.HEARING_DISABILITY
    )
    # page.locator("#UI_ADDITIONAL_CARE_NEED").select_option("4122")
    SubjectEventsNotes(page).fill_notes("updated additional care note")
    SubjectEventsNotes(page).dismiss_dialog_and_add_replacement_note()

    # Get updated supporting notes for the subject
    logging.info(
        "Retrieving updated supporting notes for the subject with NHS Number: {nhs_no}."
    )
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(screening_subject_id, type_id)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == type_id]


#     # Get the title and note from the first row of the UI table
#     ui_data = SubjectEventsNotes(page).get_title_and_note_from_row(
#     0
# )  # Row 0 is the first row
#     logging.info(f"Data from UI: {ui_data}")

#     # Get the title and note from the database
#     db_data = {
#     "title": filtered_notes_df["title"].iloc[0].strip(),
#     "note": filtered_notes_df["note"].iloc[0].strip(),
# }
#     logging.info(f"Data from DB: {db_data}")

#     # Compare the data
#     assert (
#     ui_data["title"] == db_data["title"]
#     ), f"Title does not match. UI: '{ui_data['title']}', DB: '{db_data['title']}'"
#     assert (
#     ui_data["note"] == db_data["note"]
#     ), f"Note does not match. UI: '{ui_data['note']}', DB: '{db_data['note']}'"
