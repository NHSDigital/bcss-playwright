import pytest
from playwright.sync_api import Page
from sqlalchemy import false
from classes.repositories.subject_repository import SubjectRepository
from classes.subject import subject
from conftest import general_properties
from pages.base_page import BasePage
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
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
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.reopen_surveillance_episode_page import (
    ReopenSurveillanceEpisodePage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.surveillance.produce_healthcheck_forms_page import (
    ProduceHealthCheckFormsPage,
)
from pages.surveillance.surveillance_page import SurveillancePage
from utils import screening_subject_page_searcher
from utils import generate_health_check_forms_util
from utils.appointments import (
    AppointmentAttendance,
    book_post_investigation_appointment,
)
from utils.calendar_picker import CalendarPicker
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.sspi_change_steps import SSPIChangeSteps
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
import logging
from utils.batch_processing import batch_processing
from pages.logout.log_out_page import LogoutPage
from datetime import datetime, timedelta
from classes.repositories.subject_repository import SubjectRepository
from utils.oracle.oracle_specific_functions.organisation_parameters import (
    set_org_parameter_value,
)


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

    """
    # Given I log in to BCSS "England" as user role "Screening Centre Manager at BCS001"
    user_role = UserTools.user_login(
        page, "Screening Centre Manager at BCS001", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    #    When I run surveillance invitations for 1 subject

    nhs_no = GenerateHealthCheckFormsUtil(page).invite_surveillance_subjects_early(
        general_properties["eng_screening_centre_id"]
    )
    logging.info(f"[SUBJECT RETRIEVAL] Subject's NHS Number: {nhs_no}")
    # Then my subject has been updated as follows:

    criteria = {
        "latest episode status": "Open",
        "latest episode type": "Surveillance",
        "latest event status": "X500 Selected For Surveillance",
        "responsible screening centre code": "User's screening centre",
        "subject has unprocessed sspi updates": "No",
        "subject has user dob updates": "No",
    }

    subject_assertion(nhs_no, criteria, user_role)
    # And there is a "X500" letter batch for my subject with the exact title "Surveillance Selection"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "X500", "Surveillance Selection"
    )

    # When I set the value of parameter 82 to "Y" for my organisation with immediate effect
    org_id = general_properties["eng_screening_centre_id"]
    set_org_parameter_value(82, "Y", org_id)
    # When I receive an SSPI update to change their date of birth to "72" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 72)
    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "72"})
    # When I process the open "X500" letter batch for my subject
    batch_processing(
        page,
        batch_type="X500",
        batch_description="Surveillance Selection",
    )
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X505 HealthCheck Form Printed",
        },
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
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
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I choose to book a practitioner clinic for my subject
    SubjectScreeningSummaryPage(page=page).click_book_practitioner_clinic_button()

    # And I set the practitioner appointment date to "today"
    # And I book the earliest available post investigation appointment on this date
    book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X610 Surveillance Appointment Made",
        },
    )

    # And there is a "X610" letter batch for my subject with the exact title "Surveillance Appointment Invitation Letter"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "X610", "Surveillance Appointment Invitation Letter", True
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # When I process the open "X610" letter batch for my subject
    batch_processing(
        page,
        "X610",
        "Surveillance Appointment Invitation Letter",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X615 Surveillance Appointment Invitation Letter Printed"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    # And I view the latest practitioner appointment in the subject's episode
    # And the subject DNAs the practitioner appointment
    AppointmentAttendance(page).mark_as_dna("Patient did not attend")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "X641 Patient did not attend Surveillance Appointment"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Book Surveillance Appointment"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_book_surveillance_appointment_button()
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "X600 Surveillance Appointment Required"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I choose to book a practitioner clinic for my subject
    SubjectScreeningSummaryPage(page).click_book_practitioner_clinic_button()

    # And I set the practitioner appointment date to "today"
    # And I book the earliest available post investigation appointment on this date
    book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X610 Surveillance Appointment Made",
        },
    )
    # And there is a "X610" letter batch for my subject with the exact title "Surveillance Appointment Invitation Letter"
    # When I process the open "X610" letter batch for my subject

    batch_processing(
        page,
        "X610",
        "Surveillance Appointment Invitation Letter",
    )
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X615 Surveillance Appointment Invitation Letter Printed",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_surveillance_epsiode_link()
    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "today"
    AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "X650 Patient Attended Surveillance Appointment"},
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I select the advance episode option for "Discharge from Surveillance - Clinical Decision"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_surveillance_clinical_decision_button()
    # And I complete the Discharge from Surveillance form including Screening Consultant
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(True)
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "X390 Discharge from Surveillance - Clinical Decision"},
    )
    # And there is a "X390" letter batch for my subject with the exact title "Discharge from surveillance - Clinical (letter to GP)"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "X390", "Discharge from surveillance - Clinical (letter to GP)", True
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)
    # When I process the open "X390" letter batch for my subject
    batch_processing(
        page, "X390", "Discharge from surveillance - Clinical (letter to GP)"
    )

    # Then my subject has been updated as follows:
    criteria = {
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
        "latest event status": "X379 Discharged from Surveillance - GP Letter Printed",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Calculated FOBT due date",
        "screening due date date of change": "Today",
        "screening due date reason": "Discharge from Surveillance - Clinical Decision",
        "screening status": "NOT: Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Clinical Reason",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Discharge from Surveillance - Clinical Decision",
    }
    subject_assertion(nhs_no, criteria)
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I reopen the subject's episode for "Reopen episode for correction"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenSurveillanceEpisodePage(page).click_reopen_episode_for_correction_button()

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "As at episode start",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "Null",
        "latest episode includes event code": "E63 Reopen episode for correction",
        "latest episode recall calculation method": "Episode end date",
        "latest episode recall episode type": "Null",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Open",
        "latest episode status reason": "Null",
        "latest event status": "X900 Surveillance Episode reopened",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Null",
        "screening due date date of change": "Today",
        "screening due date reason": "Reopened episode",
        "screening status": "Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Reopened episode",
        "surveillance due date": "Calculated surveillance due date",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Reopened episode",
    }
    subject_assertion(nhs_no, criteria)
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "can" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode()
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I advance the subject's episode for "Book Surveillance Appointment"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_book_surveillance_appointment_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "X600 Surveillance Appointment Required"}
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I choose to book a practitioner clinic for my subject
    SubjectScreeningSummaryPage(page=page).click_book_practitioner_clinic_button()

    # And I set the practitioner appointment date to "tomorrow"
    # And I book the earliest available post investigation appointment on this date

    tomorrow = datetime.today() + timedelta(days=1)
    book_post_investigation_appointment(
        page,
        "The Royal Hospital (Wolverhampton)",
        appointment_date=tomorrow,
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X610 Surveillance Appointment Made",
        },
    )
    # And there is a "X610" letter batch for my subject with the exact title "Surveillance Appointment Invitation Letter"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "X610", "Surveillance Appointment Invitation Letter", True
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_surveillance_epsiode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And the Screening Centre reschedules the surveillance practitioner appointment to "today"

    AppointmentDetailPage(page).click_reschedule_radio()
    AppointmentDetailPage(page).click_calendar_button()
    CalendarPicker(page).v2_calendar_picker(datetime.today())
    book_post_investigation_appointment(page, "The Royal Hospital (Wolverhampton)")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "Latest episode includes event status": "X2 Surveillance appointment rescheduled",
            "latest event status": "X610 Surveillance Appointment Made",
        },
    )
    # And there is a "X610" letter batch for my subject with the exact title "Surveillance Appointment Invitation Letter"

    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "X610", "Surveillance Appointment Invitation Letter"
    )

    # When I process the open "X610" letter batch for my subject
    batch_processing(
        page,
        "X610",
        "Surveillance Appointment Invitation Letter",
    )
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X615 Surveillance Appointment Invitation Letter Printed",
        },
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_surveillance_epsiode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And the Screening Centre reschedules the surveillance practitioner appointment to "today"
    AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())
    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X650 Patient Attended Surveillance Appointment",
        },
    )
    #    When I receive an SSPI update to change their date of birth to "73" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 73)

    # Then my subject has been updated as follows:
    criteria = {
        "subject age": "73",
    }
    subject_assertion(nhs_no, criteria)
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Discharge from Screening and Surveillance - Clinical Decision"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_screening_and_surveillance_clinical_decision_button()

    # And I complete the Discharge from Surveillance form including Screening Consultant
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(True)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X382 Discharge from Screening and Surveillance - Clinical Decision",
        },
    )

    # And there is a "X382" letter batch for my subject with the exact title "Discharge from surveillance (clinical reason) & screening (age) - letter to GP"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no,
        "X382",
        "Discharge from surveillance (clinical reason) & screening (age) - letter to GP",
        True,
    )
    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)
    # When I process the open "X382" letter batch for my subject
    batch_processing(
        page,
        "X382",
        "Discharge from surveillance (clinical reason) & screening (age) - letter to GP",
    )
    # Then my subject has been updated as follows:
    criteria = {
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
        "latest event status": "X79 Discharge from Surveillance & Screening - GP Letter Printed",
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
    }
    subject_assertion(nhs_no, criteria, user_role)
    LogoutPage(page).log_out()
