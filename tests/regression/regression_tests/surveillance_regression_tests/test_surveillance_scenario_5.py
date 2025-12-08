import pytest
from playwright.sync_api import Page
from pages.organisations.organisations_page import OrganisationSwitchPage
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
def test_scenario_3(page: Page, general_properties: dict) -> None:
    """
        Discharge below/in-age patient for no contact

        X500-X505-A99-A59-A259-A315-A361-A323-A317-A318-A380-X513-X398-X387-X377-C203 [SSCL27b] X900-X600-X615-X625-X398-X387-X377-C203 [SSCL27a]

        This scenario tests closure of a Surveillance episode on discharge for no contact, for both an in-age and (following a reopen for patient decision) a below-age subject.  It test two routes to this closure: one where contact is lost following a failed diagnostic test and referral for a second, and one following screening centre DNA of an assessment appointment.

        Because we cannot know if we will be inviting a subject who has had previous FOBT episodes, or only a bowel scope episode, it is impossible to check if they will be set to Call or Recall; we can only check that they are not longer in Surveillance status.


         Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Record patient contact – contacted, suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – no result (2.1)
    > Enter diagnostic test outcome – failed test, refer another > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 > A318 (2.5)
    > Process A318 letter batch > A380 (2.5)
    > Record patient contact – no contact, close on no contact > X513 (2.3)
    > Record discharge from surveillance > X398 (3.4)
    > Process X398 letter batch > X387 (3.4)
    > Process X387 letter batch > X377 > C203 (3.4)
    > Check recall [SSCL27b]
    > SSPI update changes subject to below-age at recall
    > Reopen episode due to subject or patient decision > X900 (3.1)
    > Invite for assessment appointment > X600 (3.1)
    > Book SSP appointment from report > X610 (3.3)
    > Process X610 letter batch > X615 (3.3)
    > Screening Centre DNA assessment appointment > X625 (3.3)
    > Record discharge from surveillance, no contact > X398 (3.4)
    > Process X398 letter batch > X387 (3.4)
    > Process X387 letter batch > X377 > C203 (3.4)
    > Check recall [SSCL27a]
    """
    # Given I log in to BCSS "England" as user role "Specialist Screening Practitioner"
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
    if user_role is None:
        raise ValueError("User role is none")

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

    # When I receive an SSPI update to change their date of birth to "62" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 62)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "62"})

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
    # And I edit the Colonoscopy Assessment Dataset for this subject

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
