import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from utils.oracle.subject_creation_util import CreateSubjectSteps
from utils.subject_assertion import subject_assertion
from utils.call_and_recall_utils import CallAndRecallUtils
import logging
from utils.batch_processing import batch_processing
from utils.fit_kit import FitKitGeneration, FitKitLogged
from pages.logout.log_out_page import LogoutPage
from datetime import datetime
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.oracle.oracle_specific_functions.organisation_parameters import (
    set_org_parameter_value,
)
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
from utils.appointments import book_post_investigation_appointment
from classes.repositories.subject_repository import SubjectRepository
from pages.base_page import BasePage
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
    ReasonForCancellationOptions,
)
from utils.subject_demographics import SubjectDemographicUtil
from pages.screening_subject_search.discharge_from_surveillance_page import (
    DischargeFromSurveillancePage,
)
from pages.screening_subject_search.reopen_fobt_screening_episode_page import (
    ReopenFOBTScreeningEpisodePage,
)


@pytest.mark.wip
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_scenario_2(page: Page, general_properties: dict) -> None:
    """
    Scenario: 2: Discharge for clinical decision (no GP letter)

    X500-X505-X600-X610-X9-X610-X615-X650-X389-C203 [SSCL28a] X900-X600-X610-X615-X650-X89-C203 [SSCL25a]

    This scenario takes both a below-age and an over-age surveillance subject from invitation through to episode closure on X379 - discharge for clinical reason, GP letter not required.  The scenario includes cancelling and rebooking of the SSP appointment, and an episode reopen.  Changes to the subject's date of birth are done manually in this scenario: note that for a Surveillance subject no warning messages are displayed if the subject is taken below or above the usual age ranges.

    Because we cannot know if we will be inviting a subject who has had previous FOBT episodes, or only a bowel scope episode, it is impossible to check if they will be set to Call or Recall; we can only check that they are not longer in Surveillance status.

    Note: parameter 82 controls whether or not a GP letter is required when a patient is discharged from Surveillance as a result of a clinical decision.  It actually defaults to Y, but it's set at SC level in the scenario to be sure it holds the correct value.  As a parameter can't be set with immediate effect through the screens, the scenario uses a direct database update to do this.

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > Set SC value of parameter 82 (GP letter required) to N
    > Process X500 letter batch > X505 (3.1)
    > Record patient contact – contacted, SSP appointment > X600 (3.1)
    > Book SSP appointment > X610 (3.3)
    > Cancel SSP appointment > X9 (3.3)
    > Rebook SSP appointment > X610 (3.3)
    > Process X610 letter batch > X615 (3.3)
    > Attend SSP appointment > X650 (3.3)
    > Manual update changes subject to below-age at recall
    > Record discharge, clinical decision > X389 > C203 (3.4)
    > Check recall [SSCL28a]
    > Reopen episode for correction > X900 (3.1)
    > Manual update changes subject to over-age at recall
    > Record patient contact – contacted, SSP appointment > X600 (3.1)
    > Book SSP appointment > X610 (3.3)
    > Process X610 letter batch > X615 (3.3)
    > Attend SSP appointment > X650 (3.3)
    > Record discharge, clinical decision > X89 > C203 (3.4)
    > Check recall [SSCL25a]
    """
    # # Given I log in to BCSS "England" as user role "Screening Centre Manager"
    # user_role = UserTools.user_login(
    #     page, "Screening Centre Manager at BCS001", return_role_type=True
    # )
    # if user_role is None:
    #     raise ValueError("User cannot be assigned to a UserRoleType")

    # # When I run surveillance invitations for 1 subject
    # org_id = general_properties["eng_screening_centre_id"]
    # nhs_no = GenerateHealthCheckFormsUtil(page).invite_surveillance_subjects_early(org_id)
    # logging.info(f"[SUBJECT RETRIEVAL] Subject's NHS Number: {nhs_no}")

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {
    #         "latest episode status": "Open",
    #         "latest episode type": "Surveillance",
    #         "latest event status": "X500 Selected For Surveillance",
    #         "responsible screening centre code": "User's screening centre",
    #         "subject has unprocessed SSPI updates": "No",
    #         "subject has user DOB updates": "No",
    #     },
    #     user_role,
    # )

    # # When I set the value of parameter 82 to "N" for my organisation with immediate effect
    # set_org_parameter_value(82, "N", org_id)

    # # And there is a "X500" letter batch for my subject with the exact title "Surveillance Selection"
    # # When I process the open "X500" letter batch for my subject
    # batch_processing(
    #     page,
    #     "X500",
    #     "Surveillance Selection",
    # )

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {"latest event status": "X505 HealthCheck Form Printed"}
    # )

    # # When I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I select the advance episode option for "Record Contact with Patient"
    # SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    # AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # # And I record contact with the subject with outcome "Invite for Surveillance practitioner clinic (assessment)"
    # ContactWithPatientPage(page).record_contact("Invite for Surveillance practitioner clinic (assessment)")

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {"latest event status": "X600 Surveillance Appointment Required"}
    # )

    # # When I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I choose to book a practitioner clinic for my subject
    # SubjectScreeningSummaryPage(page=page).click_book_practitioner_clinic_button()

    # # And I set the practitioner appointment date to "today"
    # # And I book the earliest available post investigation appointment on this date
    # book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)", 1)

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {
    #         "latest event status": "X610 Surveillance Appointment Made",
    #     },
    # )

    # # And there is a "X610" letter batch for my subject with the exact title "Surveillance Appointment Invitation Letter"
    # SubjectRepository().there_is_letter_batch_for_subject(
    #         nhs_no, "X610", "Surveillance Appointment Invitation Letter", True
    #     )

    # # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    # LogoutPage(page).log_out(close_page=False)
    # BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("The current user cannot be assigned a user role")

    nhs_no = "9771852477"

    # # And I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I view the event history for the subject's latest episode
    # SubjectScreeningSummaryPage(page).expand_episodes_list()
    # SubjectScreeningSummaryPage(page).click_first_surveillance_epsiode_link()

    # # And I view the latest practitioner appointment in the subject's episode
    # EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # # And The Screening Centre cancels the practitioner appointment with reason "Screening Centre Cancelled"
    # AppointmentDetailPage(page).check_cancel_radio()
    # AppointmentDetailPage(page).select_reason_for_cancellation_option(
    #     "Screening Centre Cancelled"
    # )

    # # And I press OK on my confirmation prompt
    # AppointmentDetailPage(page).click_save_button(accept_dialog=True)

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {
    #         "latest event status": "X9 Surveillance Appointment Cancelled Letters not Prepared",
    #     },
    # )

    # # When I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # Then I "can" postpone the subject's surveillance episode
    # SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # # And I choose to book a practitioner clinic for my subject
    # SubjectScreeningSummaryPage(page=page).click_book_practitioner_clinic_button()

    # # And I set the practitioner appointment date to "today"
    # # And I book the earliest available post investigation appointment on this date
    # book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)", 1)

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {
    #         "latest event status": "X610 Surveillance Appointment Made",
    #     },
    # )

    # # And there is a "X610" letter batch for my subject with the exact title "Surveillance Appointment Invitation Letter"
    # # When I process the open "X610" letter batch for my subject
    # batch_processing(
    #     page,
    #     "X610",
    #     "Surveillance Appointment Invitation Letter",
    # )

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {
    #         "latest event status": "X615 Surveillance Appointment Invitation Letter Printed"
    #     },
    # )

    # # When I view the subject
    # screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # # And I view the event history for the subject's latest episode
    # SubjectScreeningSummaryPage(page).expand_episodes_list()
    # SubjectScreeningSummaryPage(page).click_first_surveillance_epsiode_link()

    # # And I view the latest practitioner appointment in the subject's episode
    # EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # # And I attend the subject's practitioner appointment "today"
    # AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())

    # # Then my subject has been updated as follows:
    # subject_assertion(
    #     nhs_no,
    #     {"latest event status": "X650 Patient Attended Surveillance Appointment"},
    # )

    # # When I view the subject
    # # And I update the subject's date of birth to make them 42 years old
    # # And I update the subject's postcode to "AA1 2BB"
    # # And I save my changes to the subject's demographics
    # SubjectDemographicUtil(page).updated_subject_demographics(
    #     nhs_no,
    #     42,
    #     "AA1 2BB",
    # )

    # # Then my subject has been updated as follows:
    # subject_assertion(nhs_no, {"subject age": "42"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Discharge from Surveillance - Clinical Decision"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_surveillance_clinical_decision_button()

    # And I complete the Discharge from Surveillance form including Screening Consultant
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(True)

    # Then my subject has been updated as follows
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
            "latest episode status reason": "Discharge from Surveillance - Clinical Decision",
            "latest event status": "X389 Discharge from Surveillance - Clinical Decision",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Awaiting failsafe",
            "screening status": "NOT: Surveillance",
            "screening status date of change": "Today",
            "screening status reason": "Clinical Reason",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Discharge from Surveillance - Clinical Decision",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen episode for correction"
    SubjectScreeningSummaryPage(page).click_reopen_fobt_screening_episode_button()
    ReopenFOBTScreeningEpisodePage(page).click_reopen_episode_for_correction_button()
