from datetime import datetime
import pytest
import logging
from playwright.sync_api import Page
from classes.subject.subject import Subject
from classes.user.user import User
from pages.logout.log_out_page import LogoutPage
from utils.fit_kit import FitKitGeneration, FitKitLogged
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools
from utils.oracle.oracle import OracleDB


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_fobt_scenario_19(page: Page) -> None:
    """
    Scenario: 19: Late response receive a kit

    This scenario tests that a new "late response" episode will be created for a subject who returns a kit following a non-response episode that started more than 6 months ago - provided they are registered with an active GP practice.

    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("This user cannot be assigned to a UserRoleType")

    # And there is a subject who meets the following criteria:
    criteria = {
        "latest event status": "S44 GP Discharge for Non-response Sent (Initial Test)",
        "latest episode kit class": "FIT",
        "latest episode started": "More than 6 months ago",
        "latest episode status": "Closed",
        "latest episode type": "FOBT",
        "latest episode sub-type": "Routine",
        "has gp practice": "Yes - active",
        "subject has unprocessed sspi updates": "No",
        "subject has user dob updates": "No",
        "subject age": "Between 60 and 72",
        "subject has unlogged kits": "Yes",
        "subject hub code": "User's hub",
    }

    user = User().from_user_role_type(user_role)

    query, bind_vars = SubjectSelectionQueryBuilder().build_subject_selection_query(
        criteria=criteria,
        user=user,
        subject=Subject(),
        subjects_to_retrieve=1,
    )

    nhs_no_df = OracleDB().execute_query(query=query, parameters=bind_vars)
    nhs_no = nhs_no_df["subject_nhs_number"].iloc[0]

    # Then Comment: NHS number
    logging.info(f"[SUBJECT RETRIEVAL] Retrieved subject's NHS number: {nhs_no}")

    # When I log my subject's latest unlogged FIT kit
    fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(nhs_no, False, False)
    FitKitLogged().log_fit_kits(
        page=page,
        sample_date=datetime.now(),
        fit_kit=fit_kit,
    )

    # Then my subject has been updated as follows:
    criteria = {
        "latest episode includes event code": "E59 Initiate Opt-in/Self-referral",
        "latest episode started": "Today",
        "latest episode status": "Open",
        "latest episode type": "FOBT",
        "latest episode sub-type": "Late Responder",
        "latest episode includes event status": "S195 Receipt of  Self-referral kit",
        "latest event status": "S43 Kit Returned and Logged (Initial Test)",
        "screening due date": "Today",
        "screening due date date of change": "Today",
        "screening due date reason": "Late Response",
        "screening status": "Self-referral",
        "screening status date of change": "Today",
        "screening status reason": "Late Response",
    }
    subject_assertion(nhs_no, criteria)

    # Finally I log out of BCSS
    LogoutPage(page).log_out()
