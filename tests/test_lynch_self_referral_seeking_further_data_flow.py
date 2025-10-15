import pytest
import logging
from playwright.sync_api import Page
from classes.subject.subject import Subject
from classes.user.user import User
from pages.logout.log_out_page import LogoutPage
from utils.oracle.oracle import OracleDB, OracleSubjectTools
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.user_tools import UserTools
from pages.subject.subject_lynch_page import SubjectPage
from utils.subject_assertion import subject_assertion


@pytest.mark.wip
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.lynch_self_referral_tests
def test_lynch_self_referral_seeking_further_data_flow(page: Page) -> None:
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
    logging.info("[TEST START] test_lynch_self_referral_seeking_further_data_flow")

    # Given I log in to BCSS "England" as user role "Hub Manager"
    login_role = "Hub Manager at BCS01"

    # Log in using the string
    UserTools.user_login(page, login_role)

    # Retrieve user details using the same string
    user_details = UserTools.retrieve_user(login_role)
    user = UserTools.get_user_object(user_details)

    # And I have created a new subject ready for self-referral using OracleSubjectTools
    nhs_no = OracleSubjectTools().create_self_referral_ready_subject(
        screening_centre=user_details["hub_code"], base_age=75
    )

    logging.info(
        "[SUBJECT CREATED IN DB] created subject in the database with no screening history who is eligible to self refer"
    )

    # TODO: When I receive Lynch diagnosis "EPCAM" for a new subject in my hub aged "75" with diagnosis date "3 years ago" and last colonoscopy date "2 years ago"
    prepare_subject_with_lynch_diagnosis(
        page,
        user,
        nhs_no,
        SubjectPage.TestData.subject_age,
        SubjectPage.TestData.diagnosis_date,
        SubjectPage.TestData.last_colonoscopy_date,
    )

    # Then Comment: NHS number
    logging.info(f"[SUBJECT CREATION] Created subject's NHS number: {nhs_no}")

    # When I self refer the subject
    subject_page = SubjectPage(page)
    subject_page.self_refer_subject()
    subject_page.confirm_prompt()

    # TODO: And I press OK on my confirmation prompt
    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "today",
        "calculated surveillance due date": "Null",
        "lynch due date": "today",
        "lynch due date date of change": "Null",
        "lynch due date reason": "Self-referral",
        "previous screening status": "Lynch Surveillance",
        "screening due date": "Null",
        "screening due date date of change": "Null",
        "screening due date reason": "Null",
        "subject has lynch diagnosis": "Yes",
        "subject lower fobt age": "Default",
        "subject lower lynch age": "25",
        "screening status": "Lynch Self-referral",
        "screening status date of change": "Today",
        "screening status reason": "Self-referral",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Null",
        "surveillance due date reason": "Null",
    }

    subject_assertion(nhs_no, criteria)

    # When I set the subject to Seeking Further Data
    subject_page.set_seeking_further_data()

    # Then my subject has been updated as follows:
    criteria = {
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

    subject_assertion(nhs_no, criteria)

    # When I set the subject from Seeking Further Data back to "Lynch Self-referral"
    subject_page.set_screening_status(
        SubjectPage.TestData.screening_status_lynch_self_referral
    )

    # Then my subject has been updated as follows:
    criteria = {
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

    subject_assertion(nhs_no, criteria)
    LogoutPage(page).log_out()
    logging.info("[TEST END] test_lynch_self_referral_seeking_further_data_flow")


# Helper Functions
def prepare_subject_with_lynch_diagnosis(
    page: Page,
    user: User,
    nhs_no: str,
    age: int,
    diagnosis_date: str,
    last_colonoscopy_date: str | None = None,
) -> str:
    """
    Helper function to receive a Lynch diagnosis for a new subject.
    Args:
        page (Page): Playwright Page object for browser interaction.
        user (User): User object representing the logged-in user.
        age (int): Age of the subject.
        diagnosis_date (str): Date of the Lynch diagnosis.
        last_colonoscopy_date (str | None): Date of the last colonoscopy, if applicable.
    """

    criteria = {"nhs number": nhs_no}

    # if last_colonoscopy_date:
    #     criteria["lynch last colonoscopy date"] = last_colonoscopy_date

    query, bind_vars = SubjectSelectionQueryBuilder().build_subject_selection_query(
        criteria=criteria,
        user=user,
        subject=Subject(),
        subjects_to_retrieve=1,
    )

    nhs_no_df = OracleDB().execute_query(query, bind_vars)
    if nhs_no_df.empty:
        raise ValueError("[SUBJECT SELECTION] No subject found matching criteria.")

    nhs_no = nhs_no_df["subject_nhs_number"].iloc[0]
    logging.info(f"[SUBJECT SELECTED] NHS number: {nhs_no}")

    subject_page = SubjectPage(page)
    subject_page.receive_lynch_diagnosis(
        diagnosis_type=SubjectPage.TestData.lynch_diagnosis_type,
        age=age,
        diagnosis_date=diagnosis_date,
        last_colonoscopy_date=last_colonoscopy_date,
    )
    return nhs_no
