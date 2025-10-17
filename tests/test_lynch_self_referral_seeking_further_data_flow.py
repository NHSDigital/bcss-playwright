import pytest
import logging
from playwright.sync_api import Page
from classes.user.user import User
from classes.subject.subject import Subject
from pages.logout.log_out_page import LogoutPage
from utils.oracle.subject_selector import SubjectSelector
from utils.oracle.oracle import OracleDB
from utils.user_tools import UserTools
from pages.subject.subject_lynch_page import SubjectPage
from utils.subject_assertion import subject_assertion
from utils import screening_subject_page_searcher
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder


@pytest.mark.wip
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.lynch_self_referral_tests
def test_lynch_self_referral_seeking_further_data_flow(page: Page) -> None:

    # Temporary helper
    # The below lines down to logging.info are just for debug purposes to show the actual DB row
    # Remove them once the test is stable
    def debug_log_subject_db_row(nhs_no):
        query, bind_vars = SubjectSelectionQueryBuilder().build_subject_selection_query(
            criteria={"nhs number": nhs_no},
            user=User(),
            subject=Subject(),
            subjects_to_retrieve=1,
        )
        df = OracleDB().execute_query(query, bind_vars)
        logging.info(f"[DEBUG DB ROW] Subject DB row:\n{df.to_dict(orient='records')}")

    """
    Scenario: [BCSS-20606] Verify that a Lynch self-referred subject can be moved to 'Seeking Further Data' (due to uncertified death) and then reverted back to 'Lynch Self-referral' status.

    Steps:
    Log in as Hub Manager
    Receive Lynch diagnosis
    Self-refer subject
    Assert updates
    Set to Seeking Further Data
    Revert to Lynch Self-referral
    """
    subject_page = SubjectPage(page)

    logging.info("[TEST START] test_lynch_self_referral_seeking_further_data_flow")

    # Given I log in to BCSS "England" as user role "Hub Manager"
    login_role = "Hub Manager at BCS01"
    UserTools.user_login(page, login_role)

    # Retrieve user details and user object
    user_details = UserTools.retrieve_user(login_role)

    # When I receive Lynch diagnosis "EPCAM" for a new subject in my hub aged "75" with diagnosis date "3 years ago" and last colonoscopy date "2 years ago"
    # TODO: What is involved in receiving an "EPCAM" diagnosis? Is it covered by this code?
    # Get or create a subject suitable for Lynch self-referral
    nhs_no = SubjectSelector.get_or_create_subject_for_lynch_self_referral(
        screening_centre=user_details["hub_code"],
        base_age=75,
    )

    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    logging.info(
        "[SUBJECT CREATED IN DB] created subject in the database with no screening history who is eligible to self refer"
    )

    # Then Comment: NHS number
    logging.info(f"[SUBJECT CREATION] Created subject's NHS number: {nhs_no}")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    logging.info(f"[UI ACTION] Navigated to subject summary page for {nhs_no}")

    # # When I self refer the subject
    # # TODO: This step may not be needed as the created subject already has a status of "Self-referral"
    # subject_page.self_refer_subject()
    # logging.info("[UI ACTION] Self-referred the subject")

    # Then my subject has been updated as follows:
    self_referral_criteria = {
        # "calculated fobt due date": "Null",
        # "calculated lynch due date": "Today",
        # "calculated surveillance due date": "Null",
        # "lynch due date": "Today",
        # "lynch due date date of change": "Null",
        # "lynch due date reason": "Self-referral",
        # "previous screening status": "Lynch Surveillance",
        "screening due date": "Null",
        # "screening due date date of change": "Null",
        # "screening due date reason": "null",
        # "screening status": "Lynch Self-referral",
        # "screening status date of change": "Today",
        # "screening status reason": "Self-Referral",
        # "subject has lynch diagnosis": "Yes",
        # "subject lower fobt age": "Default",
        # "subject lower lynch age": "25",
        # "surveillance due date date of change": "Null",
        # "surveillance due date reason": "null",
        # "surveillance due date": "Null",
    }
    debug_log_subject_db_row(nhs_no)  # For debug purposes - can be removed later

    subject_assertion(nhs_no, self_referral_criteria)
    logging.info(
        "[ASSERTION PASSED] Subject details after self-referral are as expected"
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I set the subject to Seeking Further Data
    subject_page.set_seeking_further_data()

    # Then my subject has been updated as follows:
    seeking_further_data_criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "today",
        "calculated surveillance due date": "Null",
        "lynch due date": "today",
        "lynch due date date of change": "Null",
        "lynch due date reason": "Self-referral",
        "previous screening status": "Lynch Self-referral",
        "screening due date": "Null",
        "screening due date date of change": "Null",
        "screening due date reason": "Null",
        "subject has lynch diagnosis": "Yes",
        "subject lower fobt age": "Default",
        "subject lower lynch age": "25",
        "screening status": "Seeking Further Data",
        "screening status date of change": "Today",
        "screening status reason": "Uncertified Death",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Null",
        "surveillance due date reason": "Null",
    }
    debug_log_subject_db_row(nhs_no)  # For debug purposes - can be removed later

    subject_assertion(nhs_no, seeking_further_data_criteria)

    # When I set the subject from Seeking Further Data back to "Lynch Self-referral"
    subject_page.set_self_referral_screening_status()

    # Then my subject has been updated as follows:
    reverted_criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "today",
        "calculated surveillance due date": "Null",
        "lynch due date": "today",
        "lynch due date date of change": "Null",
        "lynch due date reason": "Self-referral",
        "previous screening status": "Lynch Self-referral",
        "screening due date": "Null",
        "screening due date date of change": "Null",
        "screening due date reason": "Null",
        "subject has lynch diagnosis": "Yes",
        "subject lower fobt age": "Default",
        "subject lower lynch age": "25",
        "screening status": "Lynch Self-referral",
        "screening status date of change": "Today",
        "screening status reason": "Reset seeking further data to Lynch Self-referral",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Null",
        "surveillance due date reason": "Null",
    }
    debug_log_subject_db_row(nhs_no)  # For debug purposes - can be removed later

    subject_assertion(nhs_no, reverted_criteria)

    LogoutPage(page).log_out()
    logging.info("[TEST END] test_lynch_self_referral_seeking_further_data_flow")
