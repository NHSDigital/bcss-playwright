import logging
import pytest
from playwright.sync_api import Page
from classes.repositories.general_repository import GeneralRepository
from pages.base_page import BasePage
from pages.logout.log_out_page import LogoutPage
from pages.screening_subject_search.advance_lynch_surveillance_episode_page import (
    AdvanceLynchSurveillanceEpisodePage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.lynch_utils import LynchUtils
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.lynch_regression_tests
def test_lynch_scenario_10(page: Page) -> None:
    """
    Scenario: 10 - Unsuitable for Lynch (clinical reason)

    G1-G2-G6-G12-G13-G14 in age [SSCL58a]

    This tests where a subject is invited for Lynch Surveillance but is discharged as being not suitable, based on a clinical decision.

    Scenario summary:

    > Process Lynch diagnosis for a new in-age subject suitable for immediate invitation
    > Run Lynch invitations > G1 (5.1)
    > Process G1 letter batch > G2 (5.1)
    > Review suitability for Lynch Surveillance > G6 (5.3)
    > Close Lynch Surveillance Episode (Clinical Reason) > G12 (5.3)
    > Process G12 letter batch > G13 (5.3)
    > Process G13 letter batch > G14 (5.3)
    > Check recall [SSCL58a]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager State Registered at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # When I receive Lynch diagnosis "EPCAM" for a new subject in my hub aged "25" with diagnosis date "1 year ago" and no last colonoscopy date
    nhs_no = LynchUtils(page).insert_validated_lynch_patient_from_new_subject_with_age(
        age="25",
        gene="EPCAM",
        when_diagnosis_took_place="1 year ago",
        when_last_colonoscopy_took_place="unknown",
        user_role=user_role,
    )

    # Then Comment: NHS number
    assert nhs_no is not None
    logging.info(f"[SUBJECT CREATION] Created Lynch subject with NHS number: {nhs_no}")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "Calculated FOBT due date": "Null",
            "Calculated lynch due date": "Null",
            "Calculated surveillance due date": "Null",
            "Lynch due date": "Null",
            "Lynch due date date of change": "Null",
            "Lynch due date reason": "Null",
            "Previous screening status": "Null",
            "Screening due date": "Null",
            "Screening due date date of change": "Null",
            "Screening due date reason": "Null",
            "Subject has lynch diagnosis": "Yes",
            "Subject lower FOBT age": "Default",
            "Subject lower lynch age": "25",
            "Screening status": "Lynch Surveillance",
            "Screening status date of change": "Today",
            "Screening status reason": "Eligible for Lynch Surveillance",
            "Subject age": "25",
            "Surveillance due date": "Null",
            "Surveillance due date date of change": "Null",
            "Surveillance due date reason": "Null",
        },
        user_role,
    )

    # When I set the Lynch invitation rate for all screening centres to 50
    LynchUtils(page).set_lynch_invitation_rate(rate=50)

    # And I run the Lynch invitations process
    GeneralRepository().run_lynch_invitations()

    # And my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "Calculated FOBT due date": "Null",
            "Calculated lynch due date": "Unchanged",
            "Calculated surveillance due date": "Null",
            "Lynch due date": "25th birthday",
            "Lynch due date date of change": "Today",
            "Lynch due date reason": "Selected for Lynch Surveillance",
            "Previous screening status": "Null",
            "Screening due date": "Null",
            "Screening due date date of change": "Null",
            "Screening due date reason": "Null",
            "Subject has an open episode": "Yes",
            "Subject has lynch diagnosis": "Yes",
            "Subject lower FOBT age": "Default",
            "Subject lower lynch age": "25",
            "Screening status": "Lynch Surveillance",
            "Screening status date of change": "Today",
            "Screening status reason": "Eligible for Lynch Surveillance",
            "Subject age": "25",
            "Surveillance due date": "Null",
            "Surveillance due date date of change": "Null",
            "Surveillance due date reason": "Null",
        },
    )

    # And there is a "G1" letter batch for my subject with the exact title "Lynch Surveillance Pre-invitation"
    # When I process the open "G1" letter batch for my subject
    batch_processing(page, "G1", "Lynch Surveillance Pre-invitation")

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "G2 Lynch Pre-invitation Sent"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()

    # And I advance the subject's episode for "Review suitability for Lynch Surveillance"
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_review_suitability_for_lynch_surveillance_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "G6 Review suitability for Lynch Surveillance"}
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # When I select the advance episode option for "Close Lynch Surveillance Episode (Clinical Reason)"
    # Then I get a confirmation prompt that "contains" "Please process the G12 and G13 letter batches to close this episode"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_lynch_surveillance_episode_button()
    AdvanceLynchSurveillanceEpisodePage(page).assert_dialog_text(
        "Please process the G12 and G13 letter batches to close this episode", True
    )
    AdvanceLynchSurveillanceEpisodePage(
        page
    ).click_close_lynch_surveillance_episode_clinical_reason_button()

    # Then my subject has been updated as follow
    subject_assertion(
        nhs_no,
        {
            "latest event status": "G12 Not suitable for Lynch Surveillance (Clinical Reason)"
        },
    )

    # And there is a "G12" letter batch for my subject with the exact title "Close Lynch episode (clinical reason) (letter to subject)"
    # When I process the open "G12" letter batch for my subject
    batch_processing(
        page, "G12", "Close Lynch episode (clinical reason) (letter to subject)"
    )

    # Then my subject has been updated as follow
    subject_assertion(
        nhs_no,
        {
            "latest event status": "G13 Not suitable for Lynch Surveillance (Clinical Reason), patient letter sent"
        },
    )

    # And there is a "G13" letter batch for my subject with the exact title "Close Lynch episode (clinical reason) (letter to GP)"
    # When I process the open "G13" letter batch for my subject
    batch_processing(
        page, "G13", "Close Lynch episode (clinical reason) (letter to GP)"
    )

    # Then my subject has been updated as follow
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Null",
            "calculated lynch due date": "2 years from episode end",
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Lynch non-participation",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "Lynch Surveillance",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Clinical Reason",
            "latest event status": "G14 Not suitable for Lynch Surveillance (Clinical Reason), GP letter sent",
            "lynch due date": "Calculated Lynch due date",
            "lynch due date date of change": "Today",
            "lynch due date reason": "Lynch Surveillance",
            "lynch incident episode": "Null",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Lynch Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Lynch Surveillance",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
        },
    )

    LogoutPage(page).log_out()
