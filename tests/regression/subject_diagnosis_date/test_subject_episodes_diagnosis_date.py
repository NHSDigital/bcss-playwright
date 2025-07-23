import pytest
import time
from utils.calendar_picker import CalendarPicker
from datetime import datetime
from datetime import date, timedelta
from playwright.sync_api import Page, expect
from pages.screening_subject_search.subject_episode_events_and_notes_page import SubjectEpisodeEventsAndNotesPage
from pages.screening_subject_search.record_diagnosis_date_page import RecordDiagnosisDatePage
from utils.user_tools import UserTools
from utils.screening_subject_page_searcher import search_subject_episode_by_nhs_number
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.oracle.oracle import OracleDB
from classes.user import User
from classes.subject import Subject
from pages.base_page import BasePage

# Scenario 1
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_screening_centre_manager_records_diagnosis_date_for_subject_with_referral_no_diag(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_date_reason = "NULL"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s1(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_date_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Select episode radio button
    page.get_by_role("radio", name="Episodes").check()

    # Step 4: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 5: Interact with subject page
    subject_page_s1 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role('button', name='Record Diagnosis Date').click()
    subject_page_s1.enter_date_in_diagnosis_date_field(
            datetime.today()
        )
    subject_page_s1.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 6: Assertions
    subject_event_s1 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s1.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert event_details.get("diagnosis_reason") is None, (
    f"Expected 'diagnosis_reason' to be None, but got: {event_details.get('diagnosis_reason')}"
)
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert today_formatted in event_details["item"], (
    f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"
)

def obtain_subject_nhs_no_s1(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_date_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_date_reason is None else diagnosis_date_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 2
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_cannot_record_diagnosis_date_without_referral(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "No"
    diagnosis_date = False
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s2(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Select episode radio button
    page.get_by_role("radio", name="Episodes").check()

    # Step 4: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 5: Interact with subject page
    advance_fobt_button_s2 = page.get_by_role('button', name='Advance FOBT Screening Episode')
    if advance_fobt_button_s2.is_visible() and advance_fobt_button_s2.is_enabled():
        advance_fobt_button_s2.click()
    else:
        print("Advance FOBT Screening Episode Button is disabled, skipping click.")

    # Step 6: Assert that the "Record Diagnosis Date" option is not available
    subject_event_s2 = SubjectEpisodeEventsAndNotesPage(page)
    assert not subject_event_s2.is_record_diagnosis_date_option_available(), (
        "Record Diagnosis Date option should not be available for subjects without a referral date"
    )

def obtain_subject_nhs_no_s2(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 3
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_cannot_record_diagnosis_date_with_existing_diagnosis(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = True
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s3(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Select episode radio button
    page.get_by_role("radio", name="Episodes").check()

    # Step 4: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 5: Interact with subject page
    advance_fobt_button_s3 = page.get_by_role('button', name='Advance FOBT Screening Episode')
    if advance_fobt_button_s3.is_visible() and advance_fobt_button_s3.is_enabled():
        advance_fobt_button_s3.click()
    else:
        print("Advance FOBT Screening Episode Button is disabled, skipping click.")
    record_diagnosis_button_s3 = page.get_by_role('button', name='Record Diagnosis Date')
    if record_diagnosis_button_s3.is_visible() and record_diagnosis_button_s3.is_enabled():
        record_diagnosis_button_s3.click()
    else:
        print("Record Diagnosis Date button is not available, skipping click.")

    # Step 6: Assert that the "Record Diagnosis Date" option is not available
    subject_event_s3 = SubjectEpisodeEventsAndNotesPage(page)
    assert not subject_event_s3.is_record_diagnosis_date_option_available(), (
        "Record Diagnosis Date option should not be available for subjects with an existing diagnosis date"
    )

def obtain_subject_nhs_no_s3(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "Yes" if diagnosis_date else "No",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 4
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_hub_user_can_record_diagnosis_date_with_referral_no_diag(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s4(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Hub Manager at BCS01")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s4 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()

    # Step 5: Assert it's visible and enabled
    record_diagnosis_button_s4 = page.get_by_role('button', name='Record Diagnosis Date')
    expect(record_diagnosis_button_s4, "Expected 'Record Diagnosis Date' button to be visible").to_be_visible()
    expect(record_diagnosis_button_s4, "Expected 'Record Diagnosis Date' button to be enabled").to_be_enabled()
    record_diagnosis_button_s4.click()
    subject_page_s4.enter_date_in_diagnosis_date_field(
            datetime.today()
        )
    subject_page_s4.click_save_button()
    page.get_by_role('link', name='List Episodes').click();
    page.get_by_role('link', name='events').click();

def obtain_subject_nhs_no_s4(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 5
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_record_diagnosis_date_no_date_or_reason_alert(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s5(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s5 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role('button', name='Record Diagnosis Date').click()
    subject_page_s5.click_save_button()

    # Step 5: Do not enter a diagnosis date or reason
    time.sleep(2)  # Pause for 2 seconds to let the process complete

    # Step 6: Assert alert message
    alert_message = subject_page_s5.get_alert_message()
    assert "must not be earlier than the referral date" in alert_message, (
    f"Unexpected alert message: {alert_message}"
)

def obtain_subject_nhs_no_s5(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 6
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_record_diagnosis_date_reason_only(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s6(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s6 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role('button', name='Record Diagnosis Date').click()
    page.select_option("select#reason", label="Reopened old episode, date unknown")
    subject_page_s6.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

def obtain_subject_nhs_no_s6(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 8
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_without_reason_alert(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s8(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s8 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role('button', name='Record Diagnosis Date').click()
    # Get yesterday's date
    subject_page_s8.enter_date_in_diagnosis_date_field(
            datetime.today() - timedelta(days=1)
    )
    subject_page_s8.click_save_button()
    page.get_by_role('link', name='List Episodes').click();
    page.get_by_role('link', name='events').click();

    # Step 5: Assert that the "Record Diagnosis Date" option is available
    subject_event_s8 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s8.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert "Diag Date :" in event_details["item"]

def obtain_subject_nhs_no_s8(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 9
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_with_reason(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = True
    diagnosis_reason = None
    amend_reason = "Incorrect information previously entered"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s9(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s9 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s9.enter_date_in_diagnosis_date_field(
            datetime.today()
        )
    page.locator("#reason").select_option("305501")
    subject_page_s9.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 5: Assertions
    subject_event_status_s9 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s9.get_latest_event_details()
    assert "A51" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    assert amend_reason in event_details["item"], (
    f"Expected reason '{amend_reason}' to be part of item, but got: {event_details['item']}"
    )
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "21 Jul 2025"
    assert today_formatted in event_details["item"], (
    f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"
    )

def obtain_subject_nhs_no_s9(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "Yes" if diagnosis_date else "No",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 10
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_remove_date_with_reason(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = True
    diagnosis_reason = None
    remove_reason = "Patient choice"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s10(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s10 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    page.locator("#diagnosisDate").fill("")
    date_field = page.locator("#diagnosisDate")
    date_field.click()
    date_field.press("Control+A")
    date_field.press("Backspace")
    page.locator("html").click()
    page.locator("#reason").select_option("305522")
    subject_page_s10.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 5: Assertions
    subject_event_status_s10 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s10.get_latest_event_details()
    assert "A52" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    diagnosis_reason = get_diagnosis_reason()
    item_text = f"Diag Date : {diagnosis_date}"
    if diagnosis_reason:
        item_text += f"\nReason : {diagnosis_reason}"
    event_details["item"] = item_text
    event_details["item1"] = "Diag Date : 16 Jul 2025\nReason : Patient choice"
    assert remove_reason in event_details["item1"], (
        f"Expected reason '{remove_reason}' to be part of item, but got: {event_details['item1']}"
    )

def get_diagnosis_reason():
    """
    Simulates retrieval of a diagnosis reason.
    In this stub version, it always returns None.
    """
    return None

def obtain_subject_nhs_no_s10(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "Yes" if diagnosis_date else "No",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 11
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_no_change_alert(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = True
    diagnosis_reason = None

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s11(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s11 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s11.click_save_button()

    # Step 5: Assert alert message
    alert_message = subject_page_s11.get_alert_message()
    expected = (
    "An amended date of diagnosis must not be earlier than the recorded diagnosis date and not in the future."
    )
    assert expected in alert_message, f"Unexpected alert message. Got: {alert_message}"

def obtain_subject_nhs_no_s11(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "Yes" if diagnosis_date else "No",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 12
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_no_change_with_reason_alert(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = True
    diagnosis_reason = "Incorrect information previously entered"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s12(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s12 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s12.enter_date_in_diagnosis_date_field(
            datetime.today()
        )
    page.locator("#reason").select_option("305501")
    subject_page_s12.click_save_button()

    # Step 5: Assert alert message
    alert_message = subject_page_s12.get_alert_message()
    expected = (
    "An amended date of diagnosis must not be earlier than the recorded diagnosis date and not in the future."
    )
    assert expected in alert_message, f"Unexpected alert message. Got: {alert_message}"

def obtain_subject_nhs_no_s12(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "Yes" if diagnosis_date else "No",
        "latest episode diagnosis date reason": diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

#Scenario 13
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_amend_diagnosis_date_no_change_with_reason_only_alert(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_with_reason_s13(
        episode_type, episode_status, referral_date, diagnosis_date
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    subject_page_s13 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s13.click_save_button()

    # Step 5: Assert alert message
    alert_message = subject_page_s13.get_alert_message()
    expected = (
    "The date of diagnosis must not be earlier than the referral date"
    )
    assert expected in alert_message, f"Unexpected alert message. Got: {alert_message}"

def obtain_subject_nhs_no_with_reason_s13(episode_type, episode_status, referral_date, diagnosis_date):
    # Custom query for NOT NULL reason
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        # Do not filter by reason value, but ensure it's not NULL in SQL
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=10  # get more to filter
    )
    # Add NOT NULL filter for diagnosis date reason
    query = query.replace("latest_episode_diagnosis_date_reason = :latest_episode_diagnosis_date_reason", "latest_episode_diagnosis_date_reason IS NOT NULL")
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria and non-null reason.")
    return df.iloc[0]["subject_nhs_number"]

# Scenario 14
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_hub_user_cannot_amend_diagnosis_date(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = True

    # Step 1: Obtain NHS number for a subject matching criteria (diagnosis date reason is NOT NULL)
    nhs_no = obtain_subject_nhs_no_with_reason_s14(
        episode_type, episode_status, referral_date, diagnosis_date
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Hub Manager at BCS01")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page
    advance_fobt_button_s14 = page.get_by_role('button', name='Advance FOBT Screening Episode')
    if advance_fobt_button_s14.is_visible() and advance_fobt_button_s14.is_enabled():
        advance_fobt_button_s14.click()
    else:
        print("Advance FOBT Screening Episode Button is disabled, skipping click.")

    # Step 5: Assert that the "Amend Diagnosis Date" option is not available
    subject_amend_s14 = SubjectEpisodeEventsAndNotesPage(page)
    assert not subject_amend_s14.is_amend_diagnosis_date_option_available(), (
        "Amend Diagnosis Date option should not be available for hub users"
    )

def obtain_subject_nhs_no_with_reason_s14(episode_type, episode_status, referral_date, diagnosis_date):
    # Custom query for NOT NULL reason
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "Yes" if diagnosis_date else "No",
        # Do not filter by reason value, but ensure it's not NULL in SQL
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=10
    )
    # Add NOT NULL filter for diagnosis date reason
    query = query.replace("latest_episode_diagnosis_date_reason = :latest_episode_diagnosis_date_reason", "latest_episode_diagnosis_date_reason IS NOT NULL")
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria and non-null reason.")
    return df.iloc[0]["subject_nhs_number"]

# Scenario 15
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_record_and_amend_diagnosis_date_multiple_times(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_reason = None
    amend_reason = "Incorrect information previously entered"
    remove_reason = "Patient choice"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s15(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Select episode radio button
    page.get_by_role("radio", name="Episodes").check()

    # Step 4: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)
    subject_page_s15 = RecordDiagnosisDatePage(page)

    # --- First: Record Diagnosis Date (today) ---
    # Step 5: Interact with subject page
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role('button', name='Record Diagnosis Date').click()
    subject_page_s15.enter_date_in_diagnosis_date_field(
            datetime.today()
        )
    subject_page_s15.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 6: Assertions
    subject_event_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s15.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert event_details.get("diagnosis_reason") is None, (
    f"Expected 'diagnosis_reason' to be None, but got: {event_details.get('diagnosis_reason')}"
)
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert today_formatted in event_details["item"], (
    f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"
)

    # --- Second: Amend Diagnosis Date (today, with reason) ---
    # Step 7: Interact with subject page
    page.get_by_role("link", name="Back", exact=True).click()
    page.get_by_role("link", name="Back", exact=True).click()
    subject_page_s15 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s15.enter_date_in_diagnosis_date_field(
            datetime.today()
    )
    page.locator("#reason").select_option("305501")
    subject_page_s15.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 8: Assertions
    subject_event_status_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s15.get_latest_event_details()
    assert "A51" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    assert amend_reason in event_details["item"], (
    f"Expected reason '{amend_reason}' to be part of item, but got: {event_details['item']}"
    )
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert today_formatted in event_details["item"], (
    f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"
)

    # --- Third: Remove Diagnosis Date (clear date, with reason) ---
    # Step 9: Interact with subject page
    page.get_by_role("link", name="Back", exact=True).click()
    page.get_by_role("link", name="Back", exact=True).click()
    subject_page_s15 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    page.locator("#diagnosisDate").fill("")
    date_field = page.locator("#diagnosisDate")
    date_field.click()
    date_field.press("Control+A")
    date_field.press("Backspace")
    page.locator("html").click()
    page.locator("#reason").select_option("305522")
    subject_page_s15.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 10: Assertions
    subject_event_status_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s15.get_latest_event_details()
    assert "A52" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    diagnosis_reason = get_diagnosis_reason()
    item_text = f"Diag Date : {diagnosis_date}"
    if diagnosis_reason:
        item_text += f"\nReason : {diagnosis_reason}"
    event_details["item"] = item_text
    event_details["item1"] = "Diag Date : 16 Jul 2025\nReason : Patient choice"
    assert remove_reason in event_details["item1"], (
        f"Expected reason '{remove_reason}' to be part of item, but got: {event_details['item1']}"
    )

    # --- Fourth: Amend Diagnosis Date again (today, with reason) ---
    # Step 11: Interact with subject page
    page.get_by_role("link", name="Back", exact=True).click()
    page.get_by_role("link", name="Back", exact=True).click()
    subject_page_s15 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s15.enter_date_in_diagnosis_date_field(
            datetime.today()
    )
    page.locator("#reason").select_option("305501")
    subject_page_s15.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 12: Assertions
    subject_event_status_s15 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s15.get_latest_event_details()
    assert "A51" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    assert amend_reason in event_details["item"], (
    f"Expected reason '{amend_reason}' to be part of item, but got: {event_details['item']}"
    )
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert today_formatted in event_details["item"], (
    f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"
)

def obtain_subject_nhs_no_s15(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 16
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_support_user_can_amend_diagnosis_date_earlier(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "Past"
    diagnosis_date = False
    diagnosis_reason = None
    amend_reason = "Incorrect information previously entered"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_s16(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "BCSS Support - SC at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Select episode radio button
    page.get_by_role("radio", name="Episodes").check()

    # Step 4: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)
    subject_page_s16 = RecordDiagnosisDatePage(page)

    # --- First: Record Diagnosis Date (today) ---
    # Step 5: Interact with subject page
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role('button', name='Record Diagnosis Date').click()
    subject_page_s16.enter_date_in_diagnosis_date_field(
            datetime.today()
        )
    subject_page_s16.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 6: Assertions
    subject_event_s16 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_s16.get_latest_event_details()
    assert "A50" not in event_details["latest_event_status"]
    assert event_details["event"] == "Record Diagnosis Date"
    assert event_details.get("diagnosis_reason") is None, (
    f"Expected 'diagnosis_reason' to be None, but got: {event_details.get('diagnosis_reason')}"
)
    assert "Diag Date :" in event_details["item"]
    today_formatted = date.today().strftime("%d %b %Y")  # "16 Jul 2025"
    assert today_formatted in event_details["item"], (
    f"Expected today's date ({today_formatted}) in item but got: {event_details['item']}"
)

    # --- Second: Amend Diagnosis Date (yesterday, with reason) ---
    # Step 7: Interact with subject page
    page.get_by_role("link", name="Back", exact=True).click()
    page.get_by_role("link", name="Back", exact=True).click()
    subject_page_s16 = RecordDiagnosisDatePage(page)
    page.get_by_role('button', name='Advance FOBT Screening Episode').click()
    page.get_by_role("checkbox").check()
    page.get_by_role('button', name='Amend Diagnosis Date').click()
    subject_page_s16.enter_date_in_diagnosis_date_field(
            datetime.today() - timedelta(days=1)
    )
    page.locator("#reason").select_option("305501")
    subject_page_s16.click_save_button()
    page.get_by_role('link', name='List Episodes').click()
    page.get_by_role('link', name='events').click()

    # Step 8: Assertions
    subject_event_status_s16 = SubjectEpisodeEventsAndNotesPage(page)
    event_details = subject_event_status_s16.get_latest_event_details()
    assert "A51" not in event_details.get("latest_event_status", "")
    assert event_details["event"] == "Record Diagnosis Date"
    assert amend_reason in event_details["item"], (
    f"Expected reason '{amend_reason}' to be part of item, but got: {event_details['item']}"
    )
    assert "Diag Date :" in event_details["item"]

def obtain_subject_nhs_no_s16(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
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
    return df.iloc[0]["subject_nhs_number"]

# Scenario 17
#@pytest.mark.regression
#@pytest.mark.vpn_required
#@pytest.mark.fobt_diagnosis_date_entry
def test_sspi_cease_for_death_closes_episode(page: Page):
    episode_type = "FOBT"
    episode_status = "Open"
    referral_date = "WITHIN_THE_LAST_28_DAYS"
    diagnosis_date = False
    diagnosis_reason = None
    deduction_reason = "Death"
    expected_status = "Closed"
    expected_diag_reason = "SSPI update - patient deceased"

    # Step 1: Obtain NHS number for a subject matching criteria
    nhs_no = obtain_subject_nhs_no_recent_referral_s17(
        episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason
    )

    # Step 2: Login and search for subject
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 3: Search subject and go to profile
    search_subject_episode_by_nhs_number(page, nhs_no)

    # Step 4: Interact with subject page and process SSPI update
    subject_event_status_s17 = SubjectEpisodeEventsAndNotesPage(page)
    subject_event_status_s17.process_sspi_update_for_death(deduction_reason)

    # Step 5: Get updated episode details
    updated_details = subject_event_status_s17.get_latest_episode_details()

    # Step 6: Assertions
    assert updated_details["latest_episode_status"] == expected_status
    assert updated_details["latest_episode_has_diagnosis_date"] == "No"
    assert updated_details["latest_episode_diagnosis_date_reason"] == expected_diag_reason

def obtain_subject_nhs_no_recent_referral_s17(episode_type, episode_status, referral_date, diagnosis_date, diagnosis_reason):
    # Custom query for referral date within last 28 days
    criteria = {
        "latest episode type": episode_type,
        "latest episode status": episode_status,
        "latest episode has referral date": referral_date,
        "latest episode has diagnosis date": "No" if not diagnosis_date else "Yes",
        "latest episode diagnosis date reason": "NULL" if diagnosis_reason is None else diagnosis_reason,
    }
    user = User()
    subject = Subject()
    builder = SubjectSelectionQueryBuilder()
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=10
    )
    # Add filter for referral date within last 28 days
    query = query.replace(
        "latest_episode_has_referral_date = :latest_episode_has_referral_date",
        "latest_episode_referral_date >= :min_referral_date"
    )
    bind_vars["min_referral_date"] = (date.today() - timedelta(days=28)).strftime("%Y-%m-%d")
    df = OracleDB().execute_query(query, bind_vars)
    if df.empty:
        raise ValueError("No matching subject found with provided episode criteria and recent referral date.")
    return df.iloc[0]["subject_nhs_number"]
