import pytest
from playwright.sync_api import Page
from classes.repositories.subject_repository import SubjectRepository
from conftest import general_properties
from pages.base_page import BasePage
from pages.screening_subject_search.advance_surveillance_episode_page import AdvanceSurveillanceEpisodePage
from pages.screening_subject_search.contact_with_patient_page import ContactWithPatientPage
from pages.screening_subject_search.subject_screening_summary_page import SubjectScreeningSummaryPage
from pages.surveillance.produce_healthcheck_forms_page import ProduceHealthCheckFormsPage
from pages.surveillance.surveillance_page import SurveillancePage
from utils import screening_subject_page_searcher
from utils import generate_health_check_forms_util
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.sspi_change_steps import SSPIChangeSteps
from utils.user_tools import UserTools
from utils.oracle.subject_creation_util import CreateSubjectSteps
from utils.subject_assertion import subject_assertion
import logging
from utils.batch_processing import batch_processing
from pages.logout.log_out_page import LogoutPage
from datetime import datetime
from classes.repositories.subject_repository import SubjectRepository
from utils.oracle.oracle_specific_functions.organisation_parameters import (
    set_org_parameter_value,
    check_parameter,
)

@pytest.mark.wip
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.survelliance_regression_tests
def test_scenario_1(page: Page, general_properties: dict) -> None:
    """
        Scenario: 1: Discharge for clinical decision (GP letter required)

    X500-X505-X600-X610-X615-X641-X600-X610-X615-X650-X390-X379-C203 [SSCL28b] X900-X600-X610-X2-X610-X615-X650-X382-X79-C203 [SSCL25a]

    This scenario takes both an in-age and an over-age surveillance subject from invitation through to episode closure on X379 - discharge for clinical reason, GP letter required.  The scenario includes both DNA and reschedule of the SSP appointment.  It also includes a reopen, and checks that the episode could be postponed at most points during this pathway.

    Because we cannot know if we will be inviting a subject who has had previous FOBT episodes, or only a bowel scope episode, it is impossible to check if they will be set to Call or Recall; we can only check that they are not longer in Surveillance status.

    Note: parameter 82 controls whether or not a GP letter is required when a patient is discharged from Surveillance as a result of a clinical decision.  It actually defaults to Y, but it's set at SC level in the scenario to be sure it holds the correct value.  As a parameter can't be set with immediate effect through the screens, the scenario uses a direct database update to do this.


        Scenario summary:
    >Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age
    > Process X500 letter batch > X505 (3.1)
    > Record patient contact – contacted, SSP appointment > X600 (3.1)
    > Book SSP appointment from report > X610 (3.3)
    > Process X610 letter batch > X615 (3.3)
    > Patient DNA SSP appointment > X641 (3.3)
    > Choose to book SSP appointment > X600 (3.3)
    > Book SSP appointment > X610 (3.3)
    > Process X610 letter batch > X615 (3.3)
    > Attend SSP appointment > X650 (3.3)
    > Record discharge, clinical decision, GP letter required > X390 (3.4)
    > Process X390 letter batch > X379 > C203 (3.4)
    > Check recall [SSCL28b]
    > Reopen episode for correction > X900 (3.1)
    > Record patient contact – contacted, SSP appointment > X600 (3.1)
    > Book SSP appointment from subject summary > X610 (3.3)
    > Reschedule SSP appointment > X2 > X610 (3.3)
    > Process X610 letter batch > X615 (3.3)
    > Attend SSP appointment > X650 (3.3)
    > SSPI update changes subject to over-age
    > Record discharge, clinical decision, GP letter required > X382 (3.4)
    > Process X382 letter batch > X79 > C203 (3.4)
    > Check recall [SSCL25a]

    # """
    # # Given I log in to BCSS "England" as user role "Screening Centre Manager at BCS001"
    # user_role = UserTools.user_login(
    #     page, "Screening Centre Manager at BCS001", return_role_type=True
    # )
    # if user_role is None:
    #     raise ValueError("User cannot be assigned to a UserRoleType")

    # #    When I run surveillance invitations for 1 subject

    # nhs_no = GenerateHealthCheckFormsUtil(page).invite_surveillance_subjects_early(general_properties["eng_screening_centre_id"])
    # # Then my subject has been updated as follows:

    # criteria = {
    #     "latest episode status": "Open",
    #     "latest episode type": "Surveillance",
    #     "latest event status": "X500 Selected For Surveillance",
    #     "responsible screening centre code": "User's screening centre",
    #     "subject has unprocessed sspi updates": "No",
    #     "subject has user dob updates": "No",
    # }

    # subject_assertion(nhs_no, criteria,user_role)
    # # And there is a "X500" letter batch for my subject with the exact title "Surveillance Selection"
    # SubjectRepository().there_is_letter_batch_for_subject(
    #     nhs_no, "X500", "Surveillance Selection"
    # )
    # # Then Comment: NHS number    logging.info(f"Surveillance Scenario  NHS Number: {nhs_number}")
    # # When I set the value of parameter 82 to "Y" for my organisation with immediate effect
    # org_id = general_properties["eng_screening_centre_id"]
    # set_org_parameter_value(82, "Y", org_id)
    # # When I receive an SSPI update to change their date of birth to "72" years old
    # SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 72)
    # # Then my subject has been updated as follows:
    # subject_assertion(nhs_no, {"subject age": "72"})
    # # When I process the open "X500" letter batch for my subject
    # batch_processing(
    #     page,
    #     batch_type="X500",
    #     batch_description="Surveillance Selection",
    # )
    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {
    #         "latest event status": "X505 HealthCheck Form Printed",
    #     },
    # )
    UserTools.user_login(
        page, "Screening Centre Manager at BCS001", return_role_type=True
    )
    nhs_no = '9712072282'
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        page=page, nhs_no=nhs_no
    )
    # And I select the advance episode option for "Record Contact with Patient"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()
    # And I record contact with the subject with outcome "Invite for Surveillance practitioner clinic (assessment)"
    ContactWithPatientPage(page).record_contact(
        "Invite for Surveillance practitioner clinic (assessment)"
    )
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X600 Surveillance Appointment Required",
        },
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        page=page, nhs_no=nhs_no
    )   
