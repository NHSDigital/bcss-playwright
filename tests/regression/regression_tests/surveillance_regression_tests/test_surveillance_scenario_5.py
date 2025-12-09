from datetime import datetime
import pytest
from playwright.sync_api import Page
from classes.user.user import User
from classes.repositories.person_repository import PersonRepository
from pages.datasets.investigation_dataset_page import (
    BowelPreparationQualityOptions,
    ComfortOptions,
    DrugTypeOptions,
    EndoscopyLocationOptions,
    FailureReasonsOptions,
    InsufflationOptions,
    InvestigationDatasetsPage,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    YesNoOptions,
)
from pages.organisations.organisations_page import OrganisationSwitchPage
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
)
from pages.screening_subject_search.reopen_episode_page import ReopenEpisodePage
from utils.appointments import (
    AppointmentAttendance,
    book_post_investigation_appointment,
)
from utils.calendar_picker import CalendarPicker
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.oracle.oracle import OracleDB
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
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
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
def test_scenario_5(page: Page, general_properties: dict) -> None:
    """
        Scenario: 5:Discharge below/in-age patient for no contact

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
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_colonoscopy_show_datasets()
    # And I update the Colonoscopy Assessment Dataset with the following values:
    ColonoscopyDatasetsPage(page).select_fit_for_colonoscopy_option(
        FitForColonoscopySspOptions.YES
    )
    ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()
    # And I save the Colonoscopy Assessment Dataset
    ColonoscopyDatasetsPage(page).save_dataset()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Record Contact with Patient"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with outcome "Suitable for Endoscopic Test"
    ContactWithPatientPage(page).record_contact("Suitable for Endoscopic Test")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )
    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceSurveillanceEpisodePage(page).select_test_type_dropdown_option("Colonoscopy")

    # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    AdvanceSurveillanceEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())

    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    AdvanceSurveillanceEpisodePage(page).click_invite_for_diagnostic_test_button()

    page.wait_for_timeout(500)  # Timeout to allow subject to update on the DB

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A59 Invited for Diagnostic Test",
        },
    )
    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I select the advance episode option for "Attend Diagnostic Test"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_attend_diagnostic_test_button()

    # And I attend the subject's diagnostic test today
    AttendDiagnosticTestPage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())
    AttendDiagnosticTestPage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A259 Attended Diagnostic Test"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" postpone the subject's surveillance episode
    SubjectScreeningSummaryPage(page).can_postpone_surveillance_episode(False)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    drug_information = {
        "drug_dose1": "3",
        "drug_type1": DrugTypeOptions.MANNITOL,
    }

    # And there is a clinician who meets the following criteria:
    user = User.from_user_role_type(user_role)
    criteria = {
        "Person has current role": "Accredited Screening Colonoscopist",
        "Person has current role in organisation": "User's SC",
        "Resect & Discard accreditation status": "None",
    }
    query = PersonRepository().build_person_selection_query(
        criteria=criteria, person=None, required_person_count=1, user=user, subject=None
    )
    logging.info(f"Final query: {query}")
    df = OracleDB().execute_query(query)
    person_name = (
        f"{df["person_family_name"].iloc[0]} {df["person_given_name"].iloc[0]}"
    )

    # And I set the following fields and values within the Investigation Dataset for this subject:
    general_information = {
        "practitioner": 1,
        "site": 1,
        "testing clinician": person_name,
        "aspirant endoscopist": None,
    }

    endoscopy_information = {
        "endoscope inserted": "yes",
        "procedure type": "diagnostic",
        "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
        "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
        "comfort during examination": ComfortOptions.NO_DISCOMFORT,
        "endoscopist defined extent": EndoscopyLocationOptions.DESCENDING_COLON,
        "scope imager used": YesNoOptions.YES,
        "retroverted view": YesNoOptions.NO,
        "start of intubation time": "09:00",
        "start of extubation time": "09:30",
        "end time of procedure": "10:00",
        "scope id": "Autotest",
        "insufflation": InsufflationOptions.AIR,
        "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
        "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
    }

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    failure_information = {"failure reasons": FailureReasonsOptions.PAIN}

    # And I open all minimized sections on the dataset
    # And I mark the Investigation Dataset as completed
    # When I press the save Investigation Dataset button
    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        endoscopy_information=endoscopy_information,
        drug_information=drug_information,
        general_information=general_information,
        failure_information=failure_information,
    )

    # Then the Investigation Dataset result message is "No Result"
    InvestigationDatasetsPage(page).expect_text_to_be_visible("No Result")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I select Outcome of Diagnostic Test "Failed Test - Refer Another"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.FAILED_TEST_REFER_ANOTHER
    )

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A315 Diagnostic Test Outcome Entered"},
    )
    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Other Post-investigation Contact Required"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_other_post_investigation_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A361 Other Post-investigation Contact Required"},
    )

    # When I select the advance episode option for "Record other post-investigation contact"
    AdvanceSurveillanceEpisodePage(
        page
    ).click_record_other_post_investigation_contact_button()

    # And I record contact with the subject with outcome "Post-investigation Appointment Not Required"
    ContactWithPatientPage(page).record_post_investigation_appointment_not_required()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A323 Post-investigation Appointment NOT Required",
        },
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A317 Post-investigation Contact Made ",
            "latest event status": "A318 Post-investigation Appointment NOT Required - Result Letter Created",
        },
    )

    # And there is a "A318" letter batch for my subject with the exact title "Result Letters - No Post-investigation Appointment"
    # When I process the open "A318" letter batch for my subject
    batch_processing(
        page,
        "A318",
        "Result Letters - No Post-investigation Appointment",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A380 Failed Diagnostic Test - Refer Another",
        },
    )
    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Record Contact with Patient"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with outcome "Discharge from surveillance - no contact"
    ContactWithPatientPage(page).record_contact(
        "Discharge from Surveillance - No Contact", "No"
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X513 No Patient Contact - Discharge from Surveillance"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Discharge from Surveillance - No Patient Contact"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_surveillance_no_patient_contact_button()

    # And I complete the Discharge from Surveillance form
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(False)

    # # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X398 Discharge from Surveillance - No Patient Contact"
        },
    )

    # And there is a "X398" letter batch for my subject with the exact title "Discharge from surveillance - no contact (letter to patient)"
    # When I process the open "X398" letter batch for my subject
    batch_processing(
        page,
        "X398",
        "Discharge from surveillance - no contact (letter to patient)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X387 Discharged from Surveillance - Patient Letter Printed"
        },
    )

    # And there is a "X387" letter batch for my subject with the exact title "Discharge from surveillance - no contact (letter to GP)"
    # When I process the open "X387" letter batch for my subject
    batch_processing(
        page,
        "X387",
        "Discharge from surveillance - no contact (letter to GP)",
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
        "latest episode accumulated result": "No result",
        "latest episode recall calculation method": "Episode end date",
        "latest episode recall episode type": "FOBT Screening",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Closed",
        "latest episode status reason": "Discharge from Surveillance - Cannot Contact Patient",
        "latest event status": "X377 Discharged from Surveillance - GP Letter Printed",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Calculated FOBT due date",
        "screening due date date of change": "Today",
        "screening due date reason": "Discharge from Surveillance - Cannot Contact Patient",
        "screening status": "NOT: Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Lost Patient Contact",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Discharge from Surveillance - Cannot Contact Patient",
    }
    subject_assertion(nhs_no, criteria)

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I reopen the subject's episode for "Reopen due to subject or patient decision"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenEpisodePage(page).click_reopen_due_to_subject_or_patient_decision()

    # Then my subject has been updated as follows:
    criteria = {
        "calculated fobt due date": "Null",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "As at episode start",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "No result",
        "latest episode includes event code": "E72 Reopen due to subject or patient decision",
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

    # When I receive an SSPI update to change their date of birth to "43" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 43)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "43"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I advance the subject's episode for "Book Surveillance Appointment"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_book_surveillance_appointment_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "X600 Surveillance Appointment Invited"},
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
        {"latest event status": "X610 Surveillance Appointment Made"},
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
            "latest event status": "X615 Surveillance Appointment Invitation Letter Printed "
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I view the event history for the subject's latest episode
    # And I view the latest practitioner appointment in the subject's episode
    # And the practitioner DNAs the practitioner appointment
    AppointmentAttendance(page).mark_as_dna("Practitioner did not attend")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X625 Practitioner did not attend Surveillance Appointment"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    # And I select the advance episode option for "Discharge from Surveillance - No Patient Contact"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_discharge_from_surveillance_no_patient_contact_button()
    # And I complete the Discharge from Surveillance form
    DischargeFromSurveillancePage(page).complete_discharge_from_surveillance_form(False)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X398 Discharge from Surveillance - No Patient Contact"
        },
    )
    # And there is a "X398" letter batch for my subject with the exact title "Discharge from surveillance - no contact (letter to patient)"
    # When I process the open "X398" letter batch for my subject
    batch_processing(
        page,
        "X398",
        "Discharge from surveillance - no contact (letter to patient)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X387 Discharged from Surveillance - Patient Letter Printed"
        },
    )

    # And there is a "X387" letter batch for my subject with the exact title "Discharge from surveillance - no contact (letter to GP)"
    # When I process the open "X387" letter batch for my subject
    batch_processing(
        page,
        "X387",
        "Discharge from surveillance - no contact (letter to GP)",
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
        "latest episode accumulated result": "No result",
        "latest episode recall calculation method": "Episode end date",
        "latest episode recall episode type": "FOBT Screening",
        "latest episode recall surveillance type": "Null",
        "latest episode status": "Closed",
        "latest episode status reason": "Discharge from Surveillance - Cannot Contact Patient",
        "latest event status": "X377 Discharged from Surveillance - GP Letter Printed",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Null",
        "screening due date date of change": "Today",
        "screening due date reason": "Awaiting failsafe",
        "screening status": "NOT: Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Lost Patient Contact",
        "surveillance due date": "Null",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Discharge from Surveillance - Cannot Contact Patient",
    }
    subject_assertion(nhs_no, criteria)
    
    # When I log out
    LogoutPage(page).log_out()
