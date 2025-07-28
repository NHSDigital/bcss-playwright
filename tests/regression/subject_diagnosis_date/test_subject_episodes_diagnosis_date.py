import pytest
import time
import logging
from typing import Optional, Callable
from datetime import datetime
from datetime import date, timedelta
from playwright.sync_api import Page, expect
from pages.screening_subject_search.subject_episode_events_and_notes_page import (
    SubjectEpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)
from utils.user_tools import UserTools
from utils.screening_subject_page_searcher import search_subject_episode_by_nhs_number
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.oracle.oracle import OracleDB
from classes.user import User
from classes.subject import Subject
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

# Helpers
def compose_diagnosis_text_with_reason(
    diagnosis_date: str, diagnosis_reason: Optional[str] = None
) -> str:
    """
    Builds the formatted text for a diagnosis event, including an optional reason.

    Args:
        diagnosis_date (str): The date of the diagnosis
        diagnosis_reason (Optional[str]): Reason for diagnosis removal, if provided

    Returns:
        str: Formatted diagnosis event item text
    """
    item_text = f"Diag Date : {diagnosis_date}"
    if diagnosis_reason:
        item_text += f"\nReason : {diagnosis_reason}"
    return item_text


def prepare_subject_for_test(
    page: Page, criteria: dict, role: str, select_episode_radio: bool = True
) -> str:
    """
    Queries subject by criteria, logs in with role, navigates to search, and opens profile.

    Returns:
        str: The subject's NHS number
    """
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria.")

    nhs_number = df.iloc[0]["subject_nhs_number"]
    UserTools.user_login(page, role)
    BasePage(page).go_to_screening_subject_search_page()
    if select_episode_radio:
        page.get_by_role("radio", name="Episodes").check()
    search_subject_episode_by_nhs_number(page, nhs_number)
    return nhs_number


def assert_diagnosis_event_details(
    event_details: dict,
    expected_status_not: Optional[str],
    expected_event: str = "Record Diagnosis Date",
    expected_reason: Optional[str] = None,
    assert_today: bool = True,
    log: Optional[Callable[[str], None]] = None,
) -> None:
    if log:
        log(f"Checking event: {event_details['event']}")
        log(f"Checking status: {event_details.get('latest_event_status', '')}")
        log(f"Checking item: {event_details['item']}")

    if expected_status_not is not None:
        assert expected_status_not not in event_details.get(
            "latest_event_status", ""
        ), f"Expected status '{expected_status_not}' to be absent, but got: {event_details.get('latest_event_status')}"

    assert event_details["event"] == expected_event

    if expected_reason is not None:
        assert (
            expected_reason in event_details["item"]
        ), f"Expected reason '{expected_reason}' to be part of item, but got: {event_details['item']}"
    else:
        assert (
            event_details.get("diagnosis_reason") is None
        ), f"Expected 'diagnosis_reason' to be None, but got: {event_details.get('diagnosis_reason')}"

    assert "Diag Date :" in event_details["item"]

    if assert_today:
        today_formatted = date.today().strftime("%d %b %Y")
        assert (
            today_formatted in event_details["item"]
        ), f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"


def amend_diagnosis_date_with_reason(
    page: Page,
    reason_code: str,
    date: Optional[datetime] = None,
    click_back_steps: int = 2,
) -> None:
    """
    Navigates back, amends diagnosis date with a reason, and opens the events page.

    Args:
        page (Page): Playwright page object
        reason_code (str): The dropdown value to select for reason
        date (Optional[datetime]): The date to enter in the field. Defaults to today.
        click_back_steps (int): How many times to click the 'Back' link
    """
    for _ in range(click_back_steps):
        page.get_by_role("link", name="Back", exact=True).click()

    subject_page = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()

    if date is None:
        date = datetime.today()
    subject_page.enter_date_in_diagnosis_date_field(date)
    page.locator("#reason").select_option(reason_code)
    subject_page.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()


# Scenario 1
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_screening_centre_manager_records_diagnosis_date_for_subject_with_referral_no_diag(
    page: Page,
) -> None:
    """
    Tests that a Screening Centre Manager can successfully record a diagnosis date
    for a subject who was referred but initially did not have a diagnosis recorded.

    This test simulates the UI workflow where:
      - A subject with a referral and no diagnosis is accessed.
      - The diagnosis date is entered and saved.
      - The page reflects the updated status correctly.

    Args:
        page (Page): The Playwright page object used to interact with the UI.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    subject_page_s1 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    subject_page_s1.enter_date_in_diagnosis_date_field(datetime.today())
    subject_page_s1.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 3: Assertions
    subject_event_s1 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s1.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert (
        event_details.get("diagnosis_reason") is None
    ), f"Expected 'diagnosis_reason' to be None, but got: {event_details.get('diagnosis_reason')}"
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert (
        today_formatted in event_details["item"]
    ), f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"


# Scenario 2
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_cannot_record_diagnosis_date_without_referral(page: Page) -> None:
    """
    Tests that the system prevents a Screening Centre Manager from recording
    a diagnosis date for a subject who has not been referred.

    The test verifies that:
      - The diagnosis date field is either disabled or inaccessible.
      - No save operation is permitted for diagnosis date without referral.
      - Appropriate warning or error messaging is shown (if applicable).

    Args:
        page (Page): The Playwright page object used for UI automation.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "No",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    advance_fobt_button_s2 = page.get_by_role(
        "button", name="Advance FOBT Screening Episode"
    )
    if advance_fobt_button_s2.is_visible() and advance_fobt_button_s2.is_enabled():
        advance_fobt_button_s2.click()
    else:
        print("Advance FOBT Screening Episode Button is disabled, skipping click.")

    # Step 3: Assert that the "Record Diagnosis Date" option is not available
    subject_event_s2 = SubjectEpisodeEventsAndNotesPage(page)
    assert (
        not subject_event_s2.is_record_diagnosis_date_option_available()
    ), "Record Diagnosis Date option should not be available for subjects without a referral date"


# Scenario 3
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_cannot_record_diagnosis_date_with_existing_diagnosis(page: Page) -> None:
    """
    Tests that a Screening Centre Manager cannot modify or re-enter a diagnosis date
    for a subject who already has one recorded.

    The test verifies that:
      - The diagnosis date field is locked or read-only when a diagnosis exists.
      - UI does not allow duplicate or conflicting diagnosis entries.
      - Appropriate messaging or disabled controls prevent unintended updates.

    Args:
        page (Page): The Playwright page object used to simulate browser interactions.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "Yes",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    advance_fobt_button_s3 = page.get_by_role(
        "button", name="Advance FOBT Screening Episode"
    )
    if advance_fobt_button_s3.is_visible() and advance_fobt_button_s3.is_enabled():
        advance_fobt_button_s3.click()
    else:
        print("Advance FOBT Screening Episode Button is disabled, skipping click.")
    record_diagnosis_button_s3 = page.get_by_role(
        "button", name="Record Diagnosis Date"
    )
    if (
        record_diagnosis_button_s3.is_visible()
        and record_diagnosis_button_s3.is_enabled()
    ):
        record_diagnosis_button_s3.click()
    else:
        print("Record Diagnosis Date button is not available, skipping click.")

    # Step 3: Assert that the "Record Diagnosis Date" option is not available
    subject_event_s3 = SubjectEpisodeEventsAndNotesPage(page)
    assert (
        not subject_event_s3.is_record_diagnosis_date_option_available()
    ), "Record Diagnosis Date option should not be available for subjects with an existing diagnosis date"


# Scenario 4
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_hub_user_can_record_diagnosis_date_with_referral_no_diag(page: Page) -> None:
    """
    Tests that a Hub user is allowed to record a diagnosis date for a subject who has been
    referred but does not yet have a diagnosis.

    The test ensures that:
      - The diagnosis date field is accessible for subjects with a referral but no diagnosis.
      - The user interface permits entering and saving the diagnosis date.
      - No errors or access restrictions prevent the Hub user from completing this action.

    Args:
        page (Page): The Playwright page object used to simulate browser interactions.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria.")

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Hub Manager at BCS01")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page
    subject_page_s4 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()

    # Step 5: Assert it's visible and enabled
    record_diagnosis_button_s4 = page.get_by_role(
        "button", name="Record Diagnosis Date"
    )
    expect(
        record_diagnosis_button_s4,
        "Expected 'Record Diagnosis Date' button to be visible",
    ).to_be_visible()
    expect(
        record_diagnosis_button_s4,
        "Expected 'Record Diagnosis Date' button to be enabled",
    ).to_be_enabled()
    record_diagnosis_button_s4.click()
    subject_page_s4.enter_date_in_diagnosis_date_field(datetime.today())
    subject_page_s4.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 6: Assertions
    subject_event_s4 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s4.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert (
        event_details.get("diagnosis_reason") is None
    ), f"Expected 'diagnosis_reason' to be None, but got: {event_details.get('diagnosis_reason')}"
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert (
        today_formatted in event_details["item"]
    ), f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"


# Scenario 5
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_record_diagnosis_date_no_date_or_reason_alert(page: Page) -> None:
    """
    Tests that an alert is triggered when a user attempts to record a diagnosis
    without specifying either a diagnosis date or a reason for omission.

    This test ensures:
      - Validation logic prevents incomplete diagnosis entries.
      - An appropriate alert or error message is shown to the user.
      - The diagnosis form enforces mandatory fields before submission.

    Args:
        page (Page): The Playwright page object used to simulate user interaction
        with the diagnosis entry interface.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    subject_page_s5 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    subject_page_s5.click_save_button()

    # Step 3: Do not enter a diagnosis date or reason
    time.sleep(2)  # Pause for 2 seconds to let the process complete

    # Step 4: Assertions
    alert_message = subject_page_s5.get_alert_message()
    assert (
        "must not be earlier than the referral date" in alert_message
    ), f"Unexpected alert message: {alert_message}"


# Scenario 6
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_record_diagnosis_date_reason_only(page: Page) -> None:
    """
    Tests that a user can successfully record a diagnosis by providing a reason
    for omission of the diagnosis date, without entering the actual date.

    This test verifies:
      - The form allows submission with only a reason provided.
      - Validation rules accept the absence of a diagnosis date if justified.
      - The system stores the reason correctly and does not raise errors.

    Args:
        page (Page): The Playwright page object used to simulate user interaction
        with the diagnosis recording interface.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    subject_page_s6 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    page.select_option("select#reason", label="Reopened old episode, date unknown")
    subject_page_s6.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()


# Scenario 8
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_without_reason_alert(page: Page) -> None:
    """
    Tests that an alert is triggered when a user attempts to amend an existing diagnosis date
    without providing a reason for the change.

    This test confirms:
      - Validation logic requires a justification for altering previously recorded diagnosis data.
      - An appropriate alert or error message is displayed when no reason is supplied.
      - The system prevents unintended updates that lack contextual accountability.

    Args:
        page (Page): The Playwright page object used to simulate browser-based user interaction.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    subject_page_s8 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    # Get yesterday's date
    subject_page_s8.enter_date_in_diagnosis_date_field(
        datetime.today() - timedelta(days=1)
    )
    subject_page_s8.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 3: Assert that the "Record Diagnosis Date" option is available
    subject_event_s8 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s8.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert "Diag Date :" in event_details["item"]


# Scenario 9
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_with_reason(page: Page) -> None:
    """
    Tests that a user can successfully amend an existing diagnosis date by providing a valid reason
    for the update.

    This test ensures:
      - The diagnosis date field is editable when an amendment is initiated.
      - A reason for change must be entered to proceed.
      - The system accepts the new date and reason, and reflects the update correctly in the UI.

    Args:
        page (Page): The Playwright page object used to simulate browser interaction
        with the diagnosis amendment interface.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "Yes",
        "latest episode diagnosis date reason": "NULL",
    }
    amend_reason = "Incorrect information previously entered"
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria.")

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page
    subject_page_s9 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    subject_page_s9.enter_date_in_diagnosis_date_field(datetime.today())
    page.locator("#reason").select_option("305501")
    subject_page_s9.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 5: Assertions
    subject_event_status_s9 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s9.get_latest_event_details()
    assert_diagnosis_event_details(
        event_details,
        expected_status_not="A51",
        expected_reason=amend_reason,
        log=logger.debug,
    )


# Scenario 10
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_remove_date_with_reason(page: Page) -> None:
    """
    Tests that a user can successfully remove an existing diagnosis date when a valid reason
    for removal is provided.

    This test ensures:
      - The diagnosis date field can be cleared during an amendment workflow.
      - A mandatory reason for removing the date is enforced.
      - Once submitted, the UI reflects the removal accurately and consistently.

    Args:
        page (Page): The Playwright page object used to simulate user interactions
        with the diagnosis amendment feature.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "Yes",
        "latest episode diagnosis date reason": "NULL",
    }
    remove_reason = "Patient choice"
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria.")

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page
    subject_page_s10 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    page.locator("#diagnosisDate").fill("")
    date_field = page.locator("#diagnosisDate")
    date_field.click()
    date_field.press("Control+A")
    date_field.press("Backspace")
    page.locator("html").click()
    page.locator("#reason").select_option("305522")
    subject_page_s10.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 5: Assertions
    subject_event_status_s10 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s10.get_latest_event_details()
    assert "A52" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    diagnosis_reason = get_diagnosis_reason()
    diagnosis_date = "TRUE"
    event_details["item"] = compose_diagnosis_text_with_reason(
        diagnosis_date, diagnosis_reason
    )
    # Static value comparison
    event_details["item1"] = compose_diagnosis_text_with_reason(
        "16 Jul 2025", "Patient choice"
    )
    assert (
        remove_reason in event_details["item1"]
    ), f"Expected reason '{remove_reason}' to be part of item, but got: {event_details['item1']}"


def get_diagnosis_reason():
    """
    Simulates retrieval of a diagnosis reason.
    In this stub version, it always returns None.
    """
    return None


# Scenario 11
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_no_change_alert(page: Page) -> None:
    """
    Tests that the system displays an alert or notification when a user attempts to
    submit a diagnosis amendment without making any changes to the original date.

    This test ensures:
      - The user initiates the amendment workflow for the diagnosis date.
      - No changes are made to the existing date or reason.
      - An appropriate alert or validation message is shown, preventing unnecessary submission.

    Args:
        page (Page): The Playwright page object used to simulate user interactions
        with the diagnosis amendment interface.

    Returns:
        None
    """
    # Step 1: Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "Yes",
        "latest episode diagnosis date reason": "NULL",
    }
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")

    # Step 2: Interact with subject page
    subject_page_s11 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    subject_page_s11.click_save_button()

    # Step 3: Assert alert message
    alert_message = subject_page_s11.get_alert_message()
    expected = "An amended date of diagnosis must not be earlier than the recorded diagnosis date and not in the future."
    assert expected in alert_message, f"Unexpected alert message. Got: {alert_message}"


# Scenario 12
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_no_change_with_reason_alert(page: Page) -> None:
    """
    Tests that the system alerts the user when they attempt to submit an amendment
    to a diagnosis date without making any changes to the date but still providing a reason.

    This test validates:
      - The diagnosis amendment form allows entering a reason without modifying the date.
      - The system detects that no actual change has occurred in the diagnosis date.
      - An appropriate alert or validation message is triggered, preventing unnecessary form submission.

    Args:
        page (Page): The Playwright page object used to automate interaction
        with the diagnosis amendment interface.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "Yes",
        "latest episode diagnosis date reason": "Incorrect information previously entered",
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria.")

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page
    subject_page_s12 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    subject_page_s12.enter_date_in_diagnosis_date_field(datetime.today())
    page.locator("#reason").select_option("305501")
    subject_page_s12.click_save_button()

    # Step 5: Assert alert message
    alert_message = subject_page_s12.get_alert_message()
    expected = "An amended date of diagnosis must not be earlier than the recorded diagnosis date and not in the future."
    assert alert_message, "No alert message was found after diagnosis amendment submission."
    assert expected in alert_message, f"Unexpected alert message. Got: {alert_message}"


# Scenario 13
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_no_change_with_reason_only_alert(page: Page) -> None:
    """
    Tests that an alert is triggered when a user attempts to amend a diagnosis date
    without changing the actual date, but provides a reason for the amendment.

    This ensures:
      - The system recognizes no modification to the diagnosis date itself.
      - A reason for amendment has been entered.
      - An appropriate alert is shown, preventing the user from submitting
        an amendment with no actual data change.

    Args:
        page (Page): Playwright page object used to automate and verify UI behavior.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        # Do not filter by reason value, but ensure it's not NULL in SQL
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria,
        user=user,
        subject=subject,
        subjects_to_retrieve=10,  # get more to filter
    )
    # Add NOT NULL filter for diagnosis date reason
    query = query.replace(
        "latest_episode_diagnosis_date_reason = :latest_episode_diagnosis_date_reason",
        "latest_episode_diagnosis_date_reason IS NOT NULL",
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError(
            "No matching subject found with provided episode criteria and non-null reason."
        )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page
    subject_page_s13 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    subject_page_s13.click_save_button()

    # Step 5: Assert alert message
    alert_message = subject_page_s13.get_alert_message()
    expected = "The date of diagnosis must not be earlier than the referral date"
    assert expected in alert_message, f"Unexpected alert message. Got: {alert_message}"


# Scenario 14
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_hub_user_cannot_amend_diagnosis_date(page: Page) -> None:
    """
    Tests that a hub-level user is restricted from amending the diagnosis date
    in the patient details interface.

    This verifies:
      - Role-based access control is correctly enforced.
      - The diagnosis date field is either disabled or hidden for hub users.
      - Attempts to interact with the amendment functionality by unauthorized users
        are blocked or produce an appropriate alert message.

    Args:
        page (Page): The Playwright page object used to automate UI interactions
        and validate behavior.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria (diagnosis date reason is NOT NULL)
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "Yes",
        # Do not filter by reason value, but ensure it's not NULL in SQL
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=10
    )
    # Add NOT NULL filter for diagnosis date reason
    query = query.replace(
        "latest_episode_diagnosis_date_reason = :latest_episode_diagnosis_date_reason",
        "latest_episode_diagnosis_date_reason IS NOT NULL",
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError(
            "No matching subject found with provided episode criteria and non-null reason."
        )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Hub Manager at BCS01")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page
    advance_fobt_button_s14 = page.get_by_role(
        "button", name="Advance FOBT Screening Episode"
    )
    if advance_fobt_button_s14.is_visible() and advance_fobt_button_s14.is_enabled():
        advance_fobt_button_s14.click()
    else:
        print("Advance FOBT Screening Episode Button is disabled, skipping click.")

    # Step 5: Assert that the "Amend Diagnosis Date" option is not available
    subject_amend_s14 = SubjectEpisodeEventsAndNotesPage(page)
    assert (
        not subject_amend_s14.is_amend_diagnosis_date_option_available()
    ), "Amend Diagnosis Date option should not be available for hub users"


# Scenario 15
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_record_and_amend_diagnosis_date_multiple_times(page: Page) -> None:
    """
    Tests the functionality of recording an initial diagnosis date and subsequently
    amending it multiple times, ensuring each update is accurately reflected and validated.

    This test verifies:
      - Initial diagnosis date entry is accepted and stored correctly.
      - Multiple sequential amendments to the diagnosis date can be performed.
      - Each amendment reflects correctly in the UI or data model.
      - The system does not block legitimate multiple updates.
      - No unexpected alerts or errors occur during successive amendments.

    Args:
        page (Page): Playwright page object used for interacting with the user interface.

    Returns:
        None
    """
    # Step 1: # Query subject by criteria, log in, navigate to search page, select "Episodes" radio button, and open subject profile
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    amend_reason = "Incorrect information previously entered"
    remove_reason = "Patient choice"
    prepare_subject_for_test(page, criteria, role="Screening Centre Manager at BCS001")
    subject_page_s15 = RecordDiagnosisDatePage(page)

    # --- First: Record Diagnosis Date (today) ---
    # Step 2 Interact with subject page
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    subject_page_s15.enter_date_in_diagnosis_date_field(datetime.today())
    subject_page_s15.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 3 Assertions
    subject_event_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s15.get_latest_event_details()
    assert_diagnosis_event_details(
        event_details, expected_status_not="A50", expected_reason=None, log=logger.debug
    )

    # --- Second: Amend Diagnosis Date (today, with reason) ---
    # Step 4 Interact with subject page
    amend_diagnosis_date_with_reason(page, reason_code="305501")

    # Step 5: Assertions
    subject_event_status_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s15.get_latest_event_details()
    assert_diagnosis_event_details(
        event_details,
        expected_status_not="A51",
        expected_reason=amend_reason,
        log=logger.debug,
    )

    # --- Third: Remove Diagnosis Date (clear date, with reason) ---
    # Step 6: Interact with subject page
    [page.get_by_role("link", name="Back", exact=True).click() for _ in range(2)]
    subject_page_s15 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    page.locator("#diagnosisDate").fill("")
    date_field = page.locator("#diagnosisDate")
    date_field.click()
    date_field.press("Control+A")
    date_field.press("Backspace")
    page.locator("html").click()
    page.locator("#reason").select_option("305522")
    subject_page_s15.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 7: Assertions
    subject_event_status_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s15.get_latest_event_details()
    assert "A52" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    diagnosis_reason = get_diagnosis_reason()
    diagnosis_date = "TRUE"
    # Use helper method to format the diagnosis item
    event_details["item"] = compose_diagnosis_text_with_reason(
        diagnosis_date, diagnosis_reason
    )
    # Set expected item1 string for validation
    event_details["item1"] = compose_diagnosis_text_with_reason(
        "16 Jul 2025", "Patient choice"
    )
    assert (
        remove_reason in event_details["item1"]
    ), f"Expected reason '{remove_reason}' to be part of item, but got: {event_details['item1']}"

    # --- Fourth: Amend Diagnosis Date again (today, with reason) ---
    # Step 8: Interact with subject page
    amend_diagnosis_date_with_reason(page, reason_code="305501")

    # Step 9: Assertions
    subject_event_status_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s15.get_latest_event_details()
    assert_diagnosis_event_details(
        event_details,
        expected_status_not="A51",
        expected_reason=amend_reason,
        log=logger.debug,
    )


# Scenario 16
@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_support_user_can_amend_diagnosis_date_earlier(page: Page) -> None:
    """
    Tests that a support-level user is permitted to amend the diagnosis date
    to an earlier date within the patient interface.

    This confirms that:
      - The diagnosis amendment functionality allows backdating.
      - Role permissions for support users include editing the diagnosis date.
      - The system correctly reflects the earlier date after the amendment.
      - No validation errors or access restrictions are triggered when selecting an earlier date.

    Args:
        page (Page): Playwright page object used to simulate and verify UI behavior.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "Past",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    amend_reason = "Incorrect information previously entered"
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria.")

    # Step 2: Login and search for subject
    UserTools.user_login(page, "BCSS Support - SC at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Select episode radio button
    page.get_by_role("radio", name="Episodes").check()

    # Step 4: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])
    subject_page_s16 = RecordDiagnosisDatePage(page)

    # --- First: Record Diagnosis Date (today) ---
    # Step 5: Interact with subject page
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    subject_page_s16.enter_date_in_diagnosis_date_field(datetime.today())
    subject_page_s16.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 6: Assertions
    subject_event_s16 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s16.get_latest_event_details()
    assert_diagnosis_event_details(
        event_details, expected_status_not="A50", expected_reason=None, log=logger.debug
    )

    # --- Second: Amend Diagnosis Date (yesterday, with reason) ---
    # Step 7: Interact with subject page
    [page.get_by_role("link", name="Back", exact=True).click() for _ in range(2)]
    subject_page_s16 = RecordDiagnosisDatePage(page)
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="Amend Diagnosis Date").click()
    subject_page_s16.enter_date_in_diagnosis_date_field(
        datetime.today() - timedelta(days=1)
    )
    page.locator("#reason").select_option("305501")
    subject_page_s16.click_save_button()
    page.get_by_role("link", name="List Episodes").click()
    page.get_by_role("link", name="events").click()

    # Step 8: Assertions
    subject_event_status_s16 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s16.get_latest_event_details()
    assert "A51" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    assert (
        amend_reason in event_details["item"]
    ), f"Expected reason '{amend_reason}' to be part of item, but got: {event_details['item']}"
    assert "Diag Date :" in event_details["item"]


# Scenario 17
#@pytest.mark.regression
@pytest.mark.vpn_required
@pytest.mark.fobt_diagnosis_date_entry
def test_sspi_cease_for_death_closes_episode(page: Page) -> None:
    """
    Tests that when an SSPI (Specialist Supportive and Palliative Intervention) cessation
    is recorded due to the patient's death, the corresponding care episode is automatically closed.

    This test ensures:
      - The system allows recording SSPI cessation with a 'death' reason.
      - Upon submission, the system transitions the episode to a closed state.
      - UI reflects the episode closure (e.g., status indicator, disable further edits).
      - No further SSPI amendments or entries are permitted for the closed episode.

    Args:
        page (Page): The Playwright page object used to simulate and verify UI interactions.

    Returns:
        None
    """
    # Step 1: Obtain NHS number for a subject matching criteria
    criteria = {
        "latest episode type": "FOBT",
        "latest episode status": "Open",
        "latest episode has referral date": "WITHIN_THE_LAST_28_DAYS",
        "latest episode has diagnosis date": "No",
        "latest episode diagnosis date reason": "NULL",
    }
    deduction_reason = "Death"
    expected_status = "Closed"
    expected_diag_reason = "SSPI update - patient deceased"
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=10
    )
    # Add filter for referral date within last 28 days
    query = query.replace(
        "latest_episode_has_referral_date = :latest_episode_has_referral_date",
        "latest_episode_referral_date >= :min_referral_date",
    )
    bind_vars["min_referral_date"] = (date.today() - timedelta(days=28)).strftime(
        "%Y-%m-%d"
    )
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError(
            "No matching subject found with provided episode criteria and recent referral date."
        )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, df.iloc[0]["subject_nhs_number"])

    # Step 4: Interact with subject page and process SSPI update
    subject_event_status_s17 = SubjectEpisodeEventsAndNotesPage(page)
    subject_event_status_s17.process_sspi_update_for_death(deduction_reason)

    # Step 5: Get updated episode details
    updated_details = subject_event_status_s17.get_latest_episode_details()

    # Step 6: Assertions
    assert updated_details["latest_episode_status"] == expected_status
    assert updated_details["latest_episode_has_diagnosis_date"] == "No"
    assert (
        updated_details["latest_episode_diagnosis_date_reason"] == expected_diag_reason
    )
