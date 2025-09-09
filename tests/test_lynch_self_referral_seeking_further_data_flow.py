import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from pages.base_page import BasePage
from pages.subject.subject_lynch_page import SubjectPage


@pytest.mark.regression
@pytest.mark.lynch_self_referral
def test_lynch_self_referral_seeking_further_data_flow(page: Page) -> None:
    """
    Scenario: [BCSS-20606] Move Lynch self-referred subject to seeking Further Data (uncertified death), then back
    """
    # Step 1: Log in as Hub Manager (England)
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
    BasePage(page).go_to_subjects_page()

    # Step 2: Receive Lynch diagnosis for a new subject
    subject_page = SubjectPage(
    page,
    hub_manager_role=SubjectPage.hub_manager_role,
    lynch_diagnosis_type=SubjectPage.lynch_diagnosis_type,

    subject_age=SubjectPage.subject_age,
    diagnosis_date=SubjectPage.diagnosis_date,
    last_colonoscopy_date=SubjectPage.last_colonoscopy_date,
    default_pause_seconds=SubjectPage.default_pause_seconds,
    screening_status_lynch_self_referral=SubjectPage.screening_status_lynch_self_referral,
    expected_self_referral_updates=SubjectPage.expected_self_referral_updates,
    expected_seeking_further_data_updates=SubjectPage.expected_seeking_further_data_updates,
    expected_reset_seeking_further_data_updates=SubjectPage.expected_reset_seeking_further_data_updates
)
    subject_page.receive_lynch_diagnosis(
        diagnosis_type=SubjectPage.lynch_diagnosis_type,
        age=SubjectPage.subject_age,
        diagnosis_date=SubjectPage.diagnosis_date,
        last_colonoscopy_date=SubjectPage.last_colonoscopy_date
    )
    subject_page.pause_for_processing(SubjectPage.default_pause_seconds)

    # Step 3: Self refer the subject
    subject_page.self_refer_subject()
    subject_page.confirm_prompt()
    subject_page.pause_for_processing(SubjectPage.default_pause_seconds)

    # Step 4: Assert subject updated after self-referral
    subject_page.assert_subject_updates(SubjectPage.expected_self_referral_updates)

    # Step 5: Set subject to Seeking Further Data
    subject_page.set_seeking_further_data()
    subject_page.assert_subject_updates(SubjectPage.expected_seeking_further_data_updates)

    # Step 6: Set subject back to Lynch Self-referral
    subject_page.set_screening_status(SubjectPage.screening_status_lynch_self_referral)
    subject_page.assert_subject_updates(SubjectPage.expected_reset_seeking_further_data_updates)
