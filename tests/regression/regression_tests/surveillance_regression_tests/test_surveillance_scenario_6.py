import logging
import pytest
from playwright.sync_api import Page
from pages.logout.log_out_page import LogoutPage
from pages.screening_subject_search.advance_surveillance_episode_page import (
    AdvanceSurveillanceEpisodePage,
)
from pages.screening_subject_search.discharge_from_surveillance_page import (
    DischargeFromSurveillancePage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.oracle.oracle import OracleDB
from utils.sspi_change_steps import SSPIChangeSteps
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_surveillance_scenario_6(page: Page, general_properties: dict) -> None:
    """
    Scenario: 6: Discharge over-age patient for no contact

    X500-X505-X510-X501-X381-X87-X77-C203 [SSCL25a]

    This simple scenario takes a Surveillance episode from invitation through to closure on non-response.  This gives an episode result of Surveillance non-participation (although which "flavour" is impossible to check as that depends on previous episode results).

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to over-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Run timed events > creates X505 letter (3.1)
    > Process X505 letter batch > X510 (3.1)
    > Run timed events > X501 (3.1)
    > Record discharge from surveillance, no contact > X381 (3.4)
    > Process X381 letter batch > X87 (3.4)
    > Process X87 letter batch > X77 > C203 (3.4)
    > Check recall [SSCL25a]
    """
    # Given I log in to BCSS "England" as user role "Screening Centre Manager"
    user_role = UserTools.user_login(
        page, "Screening Centre Manager at BCS001", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # When I run surveillance invitations for 1 subject
    org_id = general_properties["eng_screening_centre_id"]
    nhs_no = GenerateHealthCheckFormsUtil(page).invite_surveillance_subjects_early(
        org_id
    )
    logging.info(f"[SUBJECT RETRIEVAL] Subject's NHS Number: {nhs_no}")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode status": "Open",
            "latest episode type": "Surveillance",
            "latest event status": "X500 Selected For Surveillance",
            "responsible screening centre code": "User's screening centre",
            "subject has unprocessed SSPI updates": "No",
            "subject has user DOB updates": "No",
        },
        user_role,
    )

    # And I receive an SSPI update to change their date of birth to "75" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 75)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # And there is a "X500" letter batch for my subject with the exact title "Surveillance Selection"
    # When I process the open "X500" letter batch for my subject
    batch_processing(
        page,
        "X500",
        "Surveillance Selection",
    )

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "X505 HealthCheck Form Printed"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # Then there is a "X505" letter batch for my subject with the exact title "Surveillance Selection Reminder"
    # When I process the open "X505" letter batch for my subject
    batch_processing(
        page,
        "X505",
        "Surveillance Selection Reminder",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "X510 Surveillance Reminder Printed"}
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "X501 No Response to HealthCheck Form"}
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # And I select the advance episode option for "Discharge from Screening and Surveillance - No Patient Contact"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_screening_and_surveillance_no_patient_contact_button()

    # And I complete the Discharge from Surveillance form
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(False)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X381 Discharge from Screening and Surveillance - No Patient Contact"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)

    # And there is a "X381" letter batch for my subject with the exact title "Discharge from surveillance (no contact) & screening (age) - letter to patient"
    # When I process the open "X381" letter batch for my subject
    batch_processing(
        page,
        "X381",
        "Discharge from surveillance (no contact) & screening (age) - letter to patient",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X87 Discharged from Surveillance & Screening - Patient Letter Printed"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)

    # And there is a "X87" letter batch for my subject with the exact title "Discharge from surveillance (no contact) & screening (age) - letter to GP"
    # When I process the open "X87" letter batch for my subject
    batch_processing(
        page,
        "X87",
        "Discharge from surveillance (no contact) & screening (age) - letter to GP",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "2 years from episode end",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "Notes for subject being discharged",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "(Any) Surveillance non-participation",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Discharge from Surveillance - Age",
            "latest event status": "X77 Discharged from Surveillance & Screening - GP Letter Printed",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Outside Screening Population",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Discharge from Surveillance - Age",
        },
        user_role,
    )

    LogoutPage(page).log_out()
