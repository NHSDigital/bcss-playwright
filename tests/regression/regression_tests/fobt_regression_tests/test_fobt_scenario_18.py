import pytest
import logging
from datetime import datetime, timedelta
from playwright.sync_api import Page
from classes.repositories.episode_repository import EpisodeRepository
from classes.subject.subject import Subject
from classes.user.user import User
from pages.base_page import BasePage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
    ReasonForSymptomaticReferral,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.handover_into_symptomatic_care_page import (
    HandoverIntoSymptomaticCarePage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)
from pages.screening_subject_search.refer_to_mdt_page import ReferToMDTPage
from pages.logout.log_out_page import LogoutPage
from utils.appointments import book_appointments
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.fit_kit import FitKitGeneration, FitKitLogged
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools
from utils import screening_subject_page_searcher
from utils.oracle.oracle import OracleDB
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.datasets.investigation_dataset_page import (
    FailureReasonsOptions,
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    InsufflationOptions,
    InvestigationDatasetsPage,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    ReasonPathologyLostOptions,
    YesNoOptions,
    EndoscopyLocationOptions,
    CompletionProofOptions,
    PolypAccessOptions,
    PolypClassificationOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypInterventionModalityOptions,
    PolypInterventionRetrievedOptions,
    PolypTypeOptions,
    AdenomaSubTypeOptions,
    PolypExcisionCompleteOptions,
    PolypDysplasiaOptions,
    YesNoUncertainOptions,
)
from classes.repositories.person_repository import PersonRepository
from pages.screening_subject_search.close_fobt_screening_episode_page import (
    CloseFobtScreeningEpisodePage,
)
from pages.screening_subject_search.record_request_to_cease_page import (
    RecordRequestToCeasePage,
)
from pages.screening_subject_search.reopen_screening_episode_after_manual_cease_page import (
    ReopenScreeningEpisodeAfterManualCeasePage,
)
from pages.screening_subject_search.reopen_fobt_screening_episode_page import (
    ReopenFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from utils.subject_demographics import SubjectDemographicUtil
from utils.sspi_change_steps import SSPIChangeSteps


@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_fobt_scenario_18(page: Page) -> None:
    """
    Scenario: 18: Cancer from symptomatic procedure

    S9-S10-S43-A8-A183-(A167)-A25-J10-A99-(A50)-S92-C203 [SSCL33d] A99-A59-A259-A315-A316-A323-A317-A348-A372-A345-A346-A63-C203 [SSCL18d] [SSDOB11] [SSDOB8] A372-A345-A346-A63-C203 [SSCL19a]

    This scenario tests where a subject has a diagnostic test result of LNPCP, but then goes on to have a cancer result from symptomatic procedure.  It includes a close on interrupt in order to manually cease the subject, who is then unceased as part of the episode reopen, as well as a reopen to re-record the symptomatic result.  Recall details are checked for both an in-age and over-age subject.  In addition, updating a subject’s date of birth manually followed by an SSPI update to date of birth puts the SSPI update on hold: when the SSPI update is manually accepted, the DOB change rules are applied and the subject is ceased.

    Scenario summary:

    > Find an in-age subject at S9 whose episode started recently before today (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with ABNORMAL result > A8 (1.3)
    > Invite for colonoscopy assessment > A183 (1.11)
    > Process A183 result letter (A167) (1.11)
    > Process A183 appointment letter > A25 (1.11)
    > Attend assessment appointment > J10 (1.11)
    > Suitable for colonoscopy > A99 (1.12)
    > Manually close episode on interrupt > S92 > C203
    > Check recall [SSCL33d]
    > Manually cease subject
    > Reopen episode for patient decision > A99 (1.12)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – LNPCP (2.1)
    > Enter diagnostic test outcome – refer symptomatic > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 (2.5)
    > MDT required - record MDT > A348 (2.6)
    > Process A348 letter batch > A372 (2.6)
    > Record symptomatic result – Cancer > A345 (2.7)
    > Record diagnosis date (A50)
    > Handover into symptomatic care > A346 (2.7)
    > Process A346 letter batch > A63 (2.7) > C203 (3.6)
    > Check recall [SSCL18b]
    > Manual update changes subject to below-age
    > SSPI update would change subject to over-age (but is put on hold)
    > Accept the SSPI update to change subject to over-age
    > Check subject changes [SSDOB8]
    > Reopen to Re-record Outcome from Symptomatic Referral > A372 (2.7)
    > Record symptomatic result – Cancer > A345 (2.7)
    > Handover into symptomatic care > A346 (2.7)
    > Process A346 letter batch > A63 (2.7) > C203 (3.6)
    > Check recall [SSCL19a]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("This user cannot be assigned to a UserRoleType")

    # And there is a subject who meets the following criteria:
    criteria = {
        "latest event status": "S9 Pre-Invitation Sent",
        "latest episode kit class": "FIT",
        "latest episode started": "Within the last 6 months",
        "latest episode type": "FOBT",
        "subject age": "Between 60 and 71",
        "subject has unprocessed sspi updates": "No",
        "subject has user dob updates": "No",
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

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"
    # When I process the open "S9" letter batch for my subject
    batch_processing(
        page=page,
        batch_type="S9",
        latest_event_status="S10 - Invitation & Test Kit Sent",
        batch_description="Invitation & Test Kit (FIT)",
    )

    # When I log my subject's latest unlogged FIT kit
    fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(nhs_no, False, False)
    FitKitLogged().log_fit_kits(
        page=page,
        sample_date=datetime.now(),
        fit_kit=fit_kit,
    )

    # Then my subject has been updated as follows:
    criteria = {"latest event status": "S43 Kit Returned and Logged (Initial Test)"}
    subject_assertion(nhs_no, criteria)

    # When I read my subject's latest logged FIT kit as "ABNORMAL"
    FitKitLogged().read_latest_logged_kit(
        user=user_role, kit=fit_kit, kit_type=2, kit_result="ABNORMAL"
    )

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest event status": "A8 Abnormal"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        page=page, nhs_no=nhs_no
    )

    # And I choose to book a practitioner clinic for my subject
    SubjectScreeningSummaryPage(page).click_book_practitioner_clinic_button()

    # And I select "BCS001" as the screening centre where the practitioner appointment will be held
    # And I set the practitioner appointment date to "today"
    # And I book the "earliest" available practitioner appointment on this date
    screening_centre = "BCS001 - Wolverhampton Bowel Cancer Screening Centre"
    site = "The Royal Hospital (Wolverhampton)"

    book_appointments(
        page,
        screening_centre=screening_centre,
        site=site,
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested"
        },
    )

    # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
    # When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
    batch_processing(
        page=page,
        batch_description="Practitioner Clinic 1st Appointment",
        batch_type="A183",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A25 1st Colonoscopy Assessment Appointment Booked, letter sent"
        },
    )

    # And there is a "A183" letter batch for my subject with the exact title "GP Result (Abnormal)"
    # When I process the open "A183 - GP Result (Abnormal)" letter batch for my subject
    batch_processing(
        page=page,
        batch_type="A183",
        batch_description="GP Result (Abnormal)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A167 GP Abnormal FOBT Result Sent",
            "latest event status": "A25 1st Colonoscopy Assessment Appointment Booked, letter sent",
        },
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("The current user cannot be assigned a user role")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_fobt_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "yesterday"
    AppointmentDetailPage(page).mark_appointment_as_attended(
        datetime.today() - timedelta(1)
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "J10 1st Colonoscopy Assessment Appointment Attended"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Colonoscopy Assessment Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_colonoscopy_show_datasets()

    # And I update the Colonoscopy Assessment Dataset with the following values:
    ColonoscopyDatasetsPage(page).select_fit_for_colonoscopy_option(
        option=FitForColonoscopySspOptions.YES
    )
    ColonoscopyDatasetsPage(page).click_dataset_complete_radio_button_yes()

    # And I save the Colonoscopy Assessment Dataset
    ColonoscopyDatasetsPage(page).save_dataset()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Suitable for Endoscopic Test"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_suitable_for_endoscopic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I select the advance episode option for "Record Diagnosis Date"
    AdvanceFOBTScreeningEpisodePage(page).click_record_diagnosis_date_button()

    # And I enter a Diagnosis Date of "today"
    RecordDiagnosisDatePage(page).enter_date_in_diagnosis_date_field(datetime.today())

    # And I save Diagnosis Date Information
    RecordDiagnosisDatePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode diagnosis date reason": "Null",
            "latest episode has diagnosis date": "Yes",
            "latest episode includes event status": "A50 Diagnosis date recorded",
            "latest event status": "A99 Suitable for Endoscopic Test",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I close the subject's episode for "Opt out of current episode"
    CloseFobtScreeningEpisodePage(page).close_fobt_screening_episode(
        "Opt out of current episode"
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
            "latest episode accumulated result": "Definitive abnormal FOBT outcome",
            "latest episode recall calculation method": "S92 Interrupt Close Date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Opt out of current episode",
            "latest event status": "S92 Close Screening Episode via Interrupt",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Calculated FOBT due date",
            "screening due date date of change": "Today",
            "screening due date reason": "Recall",
            "screening status": "Recall",
            "screening status reason": "Recall",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
        },
    )

    # When I switch users to BCSS "England" as user role "Hub Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(
        page, "Hub Manager State Registered at BCS01", True
    )
    if user_role is None:
        raise ValueError("The current user cannot be assigned a user role")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I manually cease the subject with reason "No Colon (subject request)"
    SubjectScreeningSummaryPage(page).click_request_cease_button()
    RecordRequestToCeasePage(page).cease_subject_with_reason(
        "No Colon (subject request)"
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "Unchanged",
            "calculated lynch due date": "Unchanged",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "AUTO TESTING: confirm not-immediate manual cease",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Ceased",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "No Colon (subject request)",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
        },
        user_role,
    )

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("The current user cannot be assigned a user role")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I uncease my subject and reopen their episode for "Reopen due to subject or patient decision"
    SubjectScreeningSummaryPage(page).click_reopen_fobt_screening_episode_button()
    ReopenFOBTScreeningEpisodePage(
        page
    ).click_reopen_due_to_subject_or_patient_decision()
    ReopenScreeningEpisodeAfterManualCeasePage(page).fill_notes_field(
        "AUTO TEST: Manually uncease subject during episode reopen"
    )
    ReopenScreeningEpisodeAfterManualCeasePage(
        page
    ).click_uncease_and_reopen_episode_button()
    page.wait_for_timeout(500)  # Timeout to allow subject to update in the DB.

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "calculated fobt due date": "As at episode start",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Null",
            "latest episode diagnosis date reason": "Null",
            "latest episode includes event code": "E72 Reopen due to subject or patient decision",
            "latest episode recall calculation method": "S92 Interrupt Close Date",
            "latest episode recall episode type": "Null",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Open",
            "latest episode status reason": "Null",
            "latest event status": "A99 Suitable for Endoscopic Test",
            "screening due date": "Calculated FOBT due date",
            "screening due date date of change": "Today",
            "screening due date reason": "Reopened episode",
            "screening status": "NOT: Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Reopened episode",
            "surveillance due date": "Null",
            "surveillance due date reason": "Unchanged",
            "surveillance due date date of change": "Unchanged",
        },
    )

    # When I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceFOBTScreeningEpisodePage(page).select_test_type_dropdown_option(
        "Colonoscopy"
    )

    # And I enter a Diagnostic Test First Offered Appointment Date of "today"
    AdvanceFOBTScreeningEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today())

    # And I advance the subject's episode for "Invite for Diagnostic Test >>"
    AdvanceFOBTScreeningEpisodePage(page).click_invite_for_diagnostic_test_button()

    # Then my subject has been updated as follows:
    AdvanceFOBTScreeningEpisodePage(page).verify_latest_event_status_value(
        latest_event_status="A59 - Invited for Diagnostic Test"
    )

    # When I select the advance episode option for "Attend Diagnostic Test"
    AdvanceFOBTScreeningEpisodePage(page).click_attend_diagnostic_test_button()

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

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # Confirm on the investigation Datasets Page
    InvestigationDatasetsPage(page).bowel_cancer_screening_page_title_contains_text(
        "Investigation Datasets"
    )

    # And I open all minimized sections on the dataset
    InvestigationDatasetsPage(page).open_all_minimized_sections()

    # And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_drug_information(
        {
            "drug_dose1": "3",
            "drug_type1": DrugTypeOptions.MANNITOL,
        }
    )

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
    InvestigationDatasetCompletion(page).fill_out_general_information(
        {
            "practitioner": 1,
            "site": 1,
            "testing clinician": person_name,
            "aspirant endoscopist": None,
        }
    )

    InvestigationDatasetCompletion(page).fill_endoscopy_information(
        {
            "endoscope inserted": "yes",
            "procedure type": "therapeutic",
            "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
            "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
            "comfort during examination": ComfortOptions.NO_DISCOMFORT,
            "endoscopist defined extent": EndoscopyLocationOptions.APPENDIX,
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
    )

    # And I set the following completion proof values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_completion_information(
        {"completion proof": CompletionProofOptions.VIDEO_APPENDIX}
    )

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_failure_information(
        {"failure reasons": FailureReasonsOptions.NO_FAILURE_REASONS}
    )

    # And I add new polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.ANASTOMOSIS,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "11",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        1,
    )

    # And I add 1 intervention for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": PolypInterventionRetrievedOptions.YES,
        },
        1,
    )

    # And I add histology for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": 1,
            "pathologist": 1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.NOT_REPORTED,
            "polyp excision complete": PolypExcisionCompleteOptions.R1,
            "polyp size": "13",
            "polyp dysplasia": PolypDysplasiaOptions.NOT_REPORTED,
            "polyp carcinoma": YesNoUncertainOptions.NO,
        },
        1,
    )

    # And I add new polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.CAECUM,
            "classification": PolypClassificationOptions.LST_NG,
            "estimate of whole polyp size": "5",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        2,
    )

    # And I add 1 intervention for polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": PolypInterventionRetrievedOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        },
        2,
    )

    # And I add histology for polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": 1,
            "pathologist": 1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.TUBULOVILLOUS_ADENOMA,
            "polyp excision complete": PolypExcisionCompleteOptions.R1,
            "polyp size": "4",
            "polyp dysplasia": PolypDysplasiaOptions.NOT_REPORTED,
            "polyp carcinoma": YesNoUncertainOptions.NO,
        },
        2,
    )

    # And I add new polyp 3 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.HEPATIC_FLEXURE,
            "classification": PolypClassificationOptions.LST_NG,
            "estimate of whole polyp size": "21",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        3,
    )

    # And I add 1 intervention for polyp 3 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": PolypInterventionRetrievedOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
            "polyp appears fully resected endoscopically": YesNoOptions.YES,
        },
        3,
    )

    # And I add histology for polyp 3 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        },
        3,
    )

    # And I mark the Investigation Dataset as completed
    InvestigationDatasetsPage(page).check_dataset_complete_checkbox()

    # When I press the save Investigation Dataset button
    # Then the Investigation Dataset result message, which I will cancel, is "LNPCP"
    InvestigationDatasetsPage(page).click_save_dataset_button_assert_dialog("LNPCP")

    # When I press the save Investigation Dataset button
    InvestigationDatasetsPage(page).click_save_dataset_button()

    # Then I confirm the Polyp Algorithm Size for Polyp 1 is 13
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(1, "13")

    # Then I confirm the Polyp Algorithm Size for Polyp 2 is 13
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(2, "4")

    # Then I confirm the Polyp Algorithm Size for Polyp 3 is 13
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(3, "21")

    # And I confirm the Polyp Category for Polyp 1 is "Advanced colorectal polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(
        1, "Advanced colorectal polyp"
    )

    # And I confirm the Polyp Category for Polyp 2 is "Premalignant polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(2, "Premalignant polyp")

    # And I confirm the Polyp Category for Polyp 3 is "LNPCP"
    InvestigationDatasetsPage(page).assert_polyp_category(3, "LNPCP")

    # And I confirm the Episode Result is "LNPCP"
    EpisodeRepository().confirm_episode_result(nhs_no, "LNPCP")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I select Outcome of Diagnostic Test "Refer Symptomatic"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_SYMPTOMATIC
    )

    # And I select Reason for Symptomatic Referral value "Suspected Cancer Surgery"
    DiagnosticTestOutcomePage(page).select_reason_for_symptomatic_referral_option(
        ReasonForSymptomaticReferral.SUSPECTED_CANCER_SURGERY
    )

    # And I save the Diagnostic Test Outcome information
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A315 Diagnostic Test Outcome Entered"},
    )

    # When I advance the subject's episode for "Other Post-investigation Contact Required"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_other_post_investigation_button()

    # Then my subject has been updated as follows:
    AdvanceFOBTScreeningEpisodePage(page).verify_latest_event_status_value(
        "A361 - Other Post-investigation Contact Required"
    )

    # And I select the advance episode option for "Record other post-investigation contact"
    AdvanceFOBTScreeningEpisodePage(
        page
    ).click_record_other_post_investigation_contact_button()

    # And I record contact with the subject with outcome "Post-investigation Appointment Not Required"
    ContactWithPatientPage(page).record_post_investigation_appointment_not_required()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A323 Post-investigation Appointment NOT Required",
            "latest event status": "A317 Post-investigation Contact Made",
        },
    )

    # When I select the advance episode option for "MDT Referral Required"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_mdt_referral_required_button()

    # And I enter simple MDT information
    ReferToMDTPage(page).enter_date_in_mdt_discussion_date_field(datetime.today())
    ReferToMDTPage(page).select_mdt_location_lookup(1)
    ReferToMDTPage(page).click_record_mdt_appointment_button()
    page.wait_for_timeout(500)  # Timeout to allow subject to update in the DB.

    #  Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A348 MDT Referral Required"},
    )

    # And there is a "A348" letter batch for my subject with the exact title "GP Letter Indicating Referral to MDT"
    # When I process the open "A348" letter batch for my subject
    batch_processing(
        page,
        "A348",
        "GP Letter Indicating Referral to MDT",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A372 Refer Symptomatic, GP Letter Printed",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I enter a Date of Symptomatic Procedure of "yesterday"
    AdvanceFOBTScreeningEpisodePage(page).enter_date_of_symptomatic_procedure(
        datetime.today() - timedelta(days=1)
    )

    # And I advance the subject's episode for "Cancer Result, Refer MDT >>"
    AdvanceFOBTScreeningEpisodePage(page).click_cancer_result_refer_mdt_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode accumulated result": "Cancer Detected",
            "latest event status": "A345 Cancer Result, Refer MDT",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Handover into Symptomatic Care"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_handover_into_symptomatic_care_button()

    # And I fill in Handover into Symptomatic Care with Cancer details
    HandoverIntoSymptomaticCarePage(page).fill_with_cancer_details()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "A346 Handover into Symptomatic Care"}
    )

    # And there is a "A346" letter batch for my subject with the exact title "Handover into Symptomatic Care (Cancer Diagnosis)"
    # When I process the open "A346" letter batch for my subject
    batch_processing(
        page,
        "A346",
        "Handover into Symptomatic Care (Cancer Diagnosis)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "2 years from episode end",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Cancer Detected",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "A63 Cancer",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Calculated FOBT due date",
            "screening due date date of change": "Today",
            "screening due date reason": "Result referred for cancer treatment",
            "screening status": "Recall",
            "screening status reason": "Result referred for cancer treatment",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
            "symptomatic procedure date": "Yesterday",
            "symptomatic procedure result": "Cancer",
            "screening referral type": "Null",
        },
    )

    # When I view the subject
    # And I update the subject's date of birth to make them 43 years old
    # And I update the subject's postcode to "AA1 2BB"
    # And I save my changes to the subject's demographics
    # Then I get a confirmation prompt that "contains" "This change to the DoB will result in the subject falling below the eligible age for screening"
    # When I press OK on my confirmation prompt
    SubjectDemographicUtil(page).updated_subject_demographics(
        nhs_no,
        43,
        "AA1 2BB",
        "This change to the DoB will result in the subject falling below the eligible age for screening",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "2 years from episode end",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Cancer Detected",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "A63 Cancer",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Awaiting failsafe",
            "screening status": "Recall",
            "screening status date of change": "Unchanged",
            "screening status reason": "Result referred for cancer treatment",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
            "symptomatic procedure date": "Yesterday",
            "symptomatic procedure result": "Cancer",
            "screening referral type": "Null",
        },
    )

    # When I receive an SSPI update to change their date of birth to "77" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 77)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "43"})

    # When I view the subject's demographics
    # And I manually "accept" the SSPI update to the subject's "date of birth"
    # Then my alert message "equals" "Feed processed successfully"
    # When I press OK on my confirmation prompt
    SubjectDemographicUtil(page).accept_or_reject_sspi_update(
        nhs_no, True, "date of birth"
    )

    # And I pause for .5 seconds to let the process complete
    page.wait_for_timeout(500)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "2 years from episode end",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "SSPI change of DOB requires cease due to age.",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Cancer Detected",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "A63 Cancer",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Ceased",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Outside Screening Population",
            "subject age": "77",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
            "symptomatic procedure date": "Yesterday",
            "symptomatic procedure result": "Cancer",
            "screening referral type": "Null",
        },
        user_role,
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen to Re-record Outcome from Symptomatic Referral"
    SubjectScreeningSummaryPage(page).click_reopen_fobt_screening_episode_button()
    ReopenFOBTScreeningEpisodePage(
        page
    ).click_reopen_to_rerecord_outcome_from_symptomatic_referral_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "As at episode start",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "LNPCP",
            "latest episode has diagnosis date": "Yes",
            "latest episode includes event code": "E372 Reopen to Re-record Outcome from Symptomatic Referral",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "Null",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Open",
            "latest episode status reason": "Null",
            "latest event status": "A372 Refer Symptomatic, GP Letter Printed",
            "screening due date": "Calculated FOBT due date",
            "screening due date date of change": "Today",
            "screening due date reason": "Reopened episode",
            "screening status": "NOT: Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Reopened episode",
            "surveillance due date": "Null",
            "surveillance due date reason": "Unchanged",
            "surveillance due date date of change": "Unchanged",
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Null",
            "screening referral type": "Null",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I enter a Date of Symptomatic Procedure of "yesterday"
    AdvanceFOBTScreeningEpisodePage(page).enter_date_of_symptomatic_procedure(
        datetime.today() - timedelta(days=1)
    )

    # And I advance the subject's episode for "Cancer Result, Refer MDT >>"
    AdvanceFOBTScreeningEpisodePage(page).click_cancer_result_refer_mdt_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode accumulated result": "Cancer Detected",
            "latest event status": "A345 Cancer Result, Refer MDT",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Handover into Symptomatic Care"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_handover_into_symptomatic_care_button()

    # And I fill in Handover into Symptomatic Care with Cancer details
    HandoverIntoSymptomaticCarePage(page).fill_with_cancer_details()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "A346 Handover into Symptomatic Care"}
    )

    # And there is a "A346" letter batch for my subject with the exact title "Handover into Symptomatic Care (Cancer Diagnosis)"
    # When I process the open "A346" letter batch for my subject
    batch_processing(
        page,
        "A346",
        "Handover into Symptomatic Care (Cancer Diagnosis)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "2 years from episode end",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Unchanged",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "Outside screening population at recall.",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "latest episode accumulated result": "Cancer Detected",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Episode Complete",
            "latest event status": "A63 Cancer",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Ceased",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Outside Screening Population",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Unchanged",
            "surveillance due date reason": "Unchanged",
            "symptomatic procedure date": "Yesterday",
            "symptomatic procedure result": "Cancer",
            "screening referral type": "Null",
        },
        user_role,
    )

    LogoutPage(page).log_out()
