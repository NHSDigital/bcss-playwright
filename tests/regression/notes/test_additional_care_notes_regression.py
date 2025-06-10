import logging
import pytest
from playwright.sync_api import Page,expect
from pages import screening_subject_search
from pages.logout.log_out_page import LogoutPage
from pages.base_page import BasePage
from pages.screening_subject_search import subject_screening_search_page
from pages.screening_subject_search import subject_screening_summary_page
from pages.screening_subject_search.subject_screening_search_page import (SubjectScreeningPage)
from pages.screening_subject_search.subject_screening_summary_page import (SubjectScreeningSummaryPage)
from pages.screening_subject_search.subject_events_notes import SubjectEventsNotes, AdditionalCareNoteTypeOptions
from utils.user_tools import UserTools
from utils.oracle.oracle_specific_functions import get_subjects_by_note_count,get_supporting_notes


def note_types_order():
    return [
        ("Additional Care Note", 4112),
        ("Episode Note", 4110),
        ("Subject Note", 4111),
        ("Kit Note", 308015),
    ]

@pytest.mark.wip
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


def test_add_a_additional_care_note_for_a_subject_without_a_note(page: Page, smokescreen_properties: dict) -> None:
    """
    Test to add an additional care note for a subject without an existing note.
    """
    # User login
    logging.info("Starting test: Add an additional care note for a subject without a note.")
    logging.info("Logging in as 'Team Leader at BCS01'.")
    UserTools.user_login(page, "Team Leader at BCS01")

    # Navigate to the Screening Subject Search Page
    logging.info("Navigating to the Screening Subject Search Page.")
    BasePage(page).go_to_screening_subject_search_page()

    # Get a subject with no additional care notes
    subjects_df = get_subjects_by_note_count(4112)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    logging.info(f"Searching for subject with NHS Number: {nhs_no}")
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()

    # Navigate to Subject Events & Notes
    logging.info("Navigating to 'Subject Events & Notes' for the selected subject.")
    SubjectScreeningSummaryPage(page).click_subjects_events_notes()

    # Select Additional Care Note
    logging.info("Selecting 'Additional Care Needs Note'.")
    SubjectEventsNotes(page).select_additional_care_note()

    # Select Additional Care Note Type
    note_type = "Additional Care Need - Learning disability"
    logging.info(f"Selecting Additional Care Note Type: '{note_type}'.")
    SubjectEventsNotes(page).select_additional_care_note_type(AdditionalCareNoteTypeOptions.LEARNING_DISABILITY)

    # Fill Notes
    note_text = "adding additional care need notes"
    logging.info(f"Filling in notes: '{note_text}'.")
    SubjectEventsNotes(page).fill_notes(note_text)

    # Dismiss dialog and update notes
    logging.info("Dismissing dialog and clicking 'Update Notes'.")
    SubjectEventsNotes(page).dismiss_dialog_and_update_notes()

    # Navigate back
    logging.info("Navigating back to the Subject Screening Summary Page.")
    BasePage(page).click_back_button()

    # Get supporting notes for the subject
    logging.info("Retrieving supporting notes for the subject with NHS Number: {nhs_no}.")
    screening_subject_id = int(subjects_df["screening_subject_id"].iloc[0])
    logging.info(f"Screening Subject ID retrieved: {screening_subject_id}")
    type_id = int(subjects_df["type_id"].iloc[0])
    notes_df = get_supporting_notes(screening_subject_id, type_id)
    # Filter the DataFrame to only include rows where type_id == 4112
    filtered_notes_df = notes_df[notes_df["type_id"] == type_id]

    # Verify title and note match the provided values
    logging.info(
        f"Verifying that the title and note match the provided values for type_id: {type_id}.")
    assert (filtered_notes_df["title"].iloc[0].strip() == note_type), f"Title does not match. Expected: '{note_type}', Found: '{filtered_notes_df['title'].iloc[0].strip()}'."
    assert (filtered_notes_df["note"].iloc[0].strip() == note_text), f"Note does not match. Expected: '{note_text}', Found: '{filtered_notes_df['note'].iloc[0].strip()}'."

    logging.info(
        f"Verification successful: Additional care note added for the subject with NHS Number: {nhs_no}. "
        f"Title and note matched the provided values. Title: '{note_type}', Note: '{note_text}'."
    )


def test_add_additional_care_note_for_subject_with_existing_note(page: Page, smokescreen_properties: dict) -> None:
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
    subjects_df = get_subjects_by_note_count(4112,1)
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


def test_identify_subject_with_additional_care_note(page: Page, smokescreen_properties: dict) -> None:
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
    subjects_df= get_subjects_by_note_count(4112,1)
    nhs_no = subjects_df["subject_nhs_number"].iloc[0]
    SubjectScreeningPage(page).fill_nhs_number(nhs_no)
    SubjectScreeningPage(page).select_search_area_option("07")
    SubjectScreeningPage(page).click_search_button()
    # Verify subject has additional care notes  present
    logging.info("Verified: Aadditional care notes are present for the subject.")
    # logging.info("Verifying that  additional care notes are present for the subject.")
    SubjectScreeningSummaryPage(page).verify_additional_care_note_visible()


def test_view_active_additional_care_note(page: Page, smokescreen_properties: dict) -> None: 
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
    subjects_df= get_subjects_by_note_count(4112,1)
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
    # SubjectScreeningSummaryPage(page).click_additional_care_note_link()

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
      # Verify title and note match the UI values
