import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
import logging
from utils.batch_processing import batch_processing
from pages.logout.log_out_page import LogoutPage
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils import screening_subject_page_searcher
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.advance_surveillance_episode_page import (
    AdvanceSurveillanceEpisodePage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from pages.screening_subject_search.discharge_from_surveillance_page import (
    DischargeFromSurveillancePage,
)
from utils.sspi_change_steps import SSPIChangeSteps


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_surveillance_scenario_3(page: Page, general_properties: dict) -> None:
    """
    Scenario: 3: Discharge for patient decision, no diagnostic test

    X500-X505-X512-X392-X386-X376-C203 [SSCL26b]

    This scenario takes an in-age surveillance subject from invitation through to almost immediate episode closure on Discharge for patient choice.  The scenario also checks that postpone is not possible once the episode is already in a “discharge” pathway.

    This can occur right at the start of the episode (as in this scenario) or following referral for a subsequent diagnostic test where no previous diagnostic tests have achieved a result (this is covered in scenario 4).

    Because we cannot know if we will be inviting a subject who has had previous FOBT episodes, or only a bowel scope episode, it is impossible to check if they will be set to Call or Recall; we can only check that they are not longer in Surveillance status.

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Record patient contact – contacted, discharge patient choice > X512 > X392 (3.1)
    > Process X392 letter batch > X386 (3.4)
    > Process X386 letter batch > X376 > C203 (3.4)
    > Check recall [SSCL26b]
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

    # When I receive an SSPI update to change their date of birth to "65" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 65)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "65"})

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

    # And I select the advance episode option for "Record Contact with Patient"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with outcome "Discharge from surveillance - patient choice"
    ContactWithPatientPage(page).record_contact(
        "Discharge from surveillance - patient choice"
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X512 Patient Contact Resulted in Discharge from Surveillance"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Discharge from Surveillance - Patient Choice"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_surveillance_patient_choice_button()

    # And I complete the Discharge from Surveillance form
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(False)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "X392 Discharge from Surveillance - Patient Choice"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)

    # And there is a "X392" letter batch for my subject with the exact title "Discharge from surveillance - patient decision  (letter to patient)"
    # When I process the open "X392" letter batch for my subject
    batch_processing(
        page,
        "X392",
        "Discharge from surveillance - patient decision  (letter to patient)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X386 Discharged from Surveillance - Patient Letter Printed"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)

    # And there is a "X386" letter batch for my subject with the exact title "Discharge from surveillance - patient decision (letter to GP)"
    # When I process the open "X386" letter batch for my subject
    batch_processing(
        page,
        "X386",
        "Discharge from surveillance - patient decision (letter to GP)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "2 years from episode end",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "(Any) Surveillance non-participation",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Discharge from Surveillance - Patient Choice",
            "latest event status": "X376 Discharged from Surveillance - GP Letter Printed",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Calculated FOBT due date",
            "screening due date reason": "Discharge from Surveillance - Patient Choice",
            "screening due date date of change": "Today",
            "screening status": "NOT: Surveillance",
            "screening status date of change": "Today",
            "screening status reason": "Patient Choice",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Discharge from Surveillance - Patient Choice",
        },
        user_role,
    )

    LogoutPage(page).log_out()
