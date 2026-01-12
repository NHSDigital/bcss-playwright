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
from utils.oracle.oracle import OracleDB
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.lynch_regression_tests
def test_lynch_scenario_11(page: Page) -> None:
    """
    Scenario: 11 - Normal result from diagnostic tests

    G1-G2-G3-A183-A25-J10-A99-A59-A259-A315-A361-A323-A317-A318-S61 Ceased over age [SSCL11e]

    This scenario tests progression of a Lynch episode to closure on S61 Normal from diagnostic test results.

    Scenario summary:

    > Process Lynch diagnosis for a new in-age subject suitable for immediate invitation
    > Run Lynch invitations > G1 (5.1)
    > Process G1 letter batch > G2 (5.1)
    > Run timed events > G3 (5.1)
    > SSPI update changes subject to over-age at recall
    > Book appointment > A183 (1.11)
    > Process A183 letter batch > A25 (1.11)
    > Attend appointment > J10 (1.12)
    > Suitable for Endoscopic Test > A99 (2.1)
    > Invite for Diagnostic Test > A59 (2.1)
    > Attend test > A259 (2.1)
    > Diagnostic Test Outcome Entered (Normal (No Abnormalities Found)) > A315 (2.1)
    > Other Post-investigation Contact Required > A361 (2.1)
    > Post-investigation Appointment Not Required > A318 (2.1)
    > Process A318 letter batch > S61 (2.1)
    > Check recall [SSCL11e]
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

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)
    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "G3 Lynch Invitation DueThen my subject has been updated as follows:"})
