import pytest
import logging
from datetime import datetime, timedelta
from playwright.sync_api import Page
from classes.subject.subject import Subject
from classes.user.user import User
from classes.repositories.subject_repository import SubjectRepository
from utils.calendar_picker import CalendarPicker
from utils.user_tools import UserTools
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.subject_assertion import subject_assertion
from utils.fit_kit import FitKitLogged, FitKitGeneration
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.appointments import book_appointments, book_post_investigation_appointment
from utils.oracle.oracle import OracleDB
from utils.investigation_dataset import InvestigationDatasetCompletion
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
    ReferralProcedureType,
    ReasonForOnwardReferral,
)
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.logout.log_out_page import LogoutPage
from pages.base_page import BasePage
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.datasets.investigation_dataset_page import (
    InvestigationDatasetsPage,
    FailureReasonsOptions,
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    InsufflationOptions,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    YesNoOptions,
    PolypAccessOptions,
    PolypClassificationOptions,
    EndoscopyLocationOptions,
    CompletionProofOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypInterventionModalityOptions,
    PolypInterventionRetrievedOptions,
    PolypTypeOptions,
    AdenomaSubTypeOptions,
    PolypExcisionCompleteOptions,
    PolypDysplasiaOptions,
    YesNoUncertainOptions,
    ReasonPathologyLostOptions,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from classes.repositories.person_repository import PersonRepository
from classes.repositories.episode_repository import EpisodeRepository
from utils.sspi_change_steps import SSPIChangeSteps
from utils.appointments import AppointmentAttendance


@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_scenario_16(page: Page) -> None:
    """
    Scenario: 16: Close on existing LNPCP result (subject contacted)

    S9-S10-S43-A8-A183-A25-(A167)-(A50)-J11-A25-J10-A99-A59-A259-A315-A360-A410-A415-A416-A316-A430-A395-A401-A157-C203 [SSCL52a]

    This scenario tests where a subject has had one diagnostic test and been referred for a second, but then the subject declines further tests and the episode is closed on the existing result of LNPCP.  The recall settings are tested for a below-age subject, which in this case are the same as for an in-age subject.  Unlike FOBT screening which uses "awawiting failsafe" to put a below-age subject on hold until they reach the age range again, when recalling a subject to surveillance there is no concept of them being "too young".  In theory, surveillance subjects are monitored much more closely by screening centres, who will manually make any necessary adjustments.

    Scenario summary:

    > Find an in-age subject at S9 whose episode started recently before today (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with ABNORMAL result > A8 (1.3)
    > Invite for colonoscopy assessment > A183 (1.11)
    > Process A183 appointment letter > A25 (1.11)
    > Process A183 result letter (A167) (1.11)
    > Record diagnosis date (A50)
    > Patient DNA appointment > J11 (1.11)
    > Redirect to establish attendance at appointment > A25 (1.11)
    > Attend assessment appointment > J10 (1.11)
    > Suitable for colonoscopy > A99 (1.12)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – LNPCP (2.1)
    > Enter diagnostic test outcome – refer another test > A315 (2.1)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 > A316 > A430 (2.4)
    > Process A430 letter batch > A395 (2.4)
    > Record patient contact – contacted, close with existing result > A401 (2.2)
    > Process A401 letter batch > A157 (2.2) > C203 (1.13)
    > Check recall [SSCL52a]
    """
    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("The current user cannot be assigned to a UserRoleType")

    # And there is a subject who meets the following criteria:
    query, bind_vars = SubjectSelectionQueryBuilder().build_subject_selection_query(
        criteria={
            "latest event status": "S9 Pre-Invitation Sent",
            "latest episode kit class": "FIT",
            "latest episode started": "Within the last 6 months",
            "latest episode type": "FOBT",
            "subject age": "Between 60 and 71",
            "subject has unprocessed sspi updates": "No",
            "subject has user dob updates": "No",
            "subject hub code": "User's hub",
        },
        user=User().from_user_role_type(user_role),
        subject=Subject(),
        subjects_to_retrieve=1,
    )

    nhs_no_df = OracleDB().execute_query(query=query, parameters=bind_vars)
    nhs_no = nhs_no_df["subject_nhs_number"].iloc[0]

    # Then Comment: NHS number
    logging.info(f"[SUBJECT RETRIEVAL] Retrieved subject's NHS number: {nhs_no}")

    # When I receive an SSPI update to change their date of birth to "45" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 45)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "45"})

    # When I run Timed Events for my subject
    OracleDB().exec_bcss_timed_events(nhs_number=nhs_no)

    # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"
    # When I process the open "S9" letter batch for my subject
    batch_processing(
        page,
        "S9",
        "Invitation & Test Kit (FIT)",
        "S10 - Invitation & Test Kit Sent",
    )

    # When I log my subject's latest unlogged FIT kit
    fit_kit = FitKitGeneration().get_fit_kit_for_subject_sql(
        nhs_no=nhs_no, logged=False, read=False
    )
    FitKitLogged().log_fit_kits(page=page, fit_kit=fit_kit, sample_date=datetime.now())

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "S43 Kit Returned and Logged (Initial Test)"},
    )

    # When I read my subject's latest logged FIT kit as "ABNORMAL"
    FitKitLogged().read_latest_logged_kit(user_role, 2, fit_kit, "ABNORMAL")

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
    book_appointments(
        page=page,
        screening_centre="BCS001 - Wolverhampton Bowel Cancer Screening Centre",
        site="The Royal Hospital (Wolverhampton)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_number=nhs_no,
        criteria={
            "latest event status": "A183 1st Colonoscopy Assessment Appointment Requested"
        },
    )

    # And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
    # When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
    # Then my subject has been updated as follows:
    batch_processing(
        page,
        "A183",
        "Practitioner Clinic 1st Appointment",
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
        page,
        "A183",
        "GP Result (Abnormal)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A167 GP Abnormal FOBT Result Sent",
            "latest event status": "A25 1st Colonoscopy Assessment Appointment Booked, letter sent",
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
    criteria = {
        "latest episode diagnosis date reason": "Null",
        "latest episode has diagnosis date": "Yes",
        "latest episode includes event status": "A50 Diagnosis date recorded",
        "latest event status": "A25 1st Colonoscopy Assessment Appointment Booked, letter sent",
    }
    subject_assertion(nhs_number=nhs_no, criteria=criteria)

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("The current user cannot be assigned a user role")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    # And I view the latest practitioner appointment in the subject's episode
    # And The subject DNAs the practitioner appointment
    AppointmentAttendance(page).mark_as_dna("Patient did not attend")

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "J11 1st Colonoscopy Assessment Appointment Non-attendance (Patient)",
        },
    )

    # And there is a "J11" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment Non Attendance (Patient)"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no, "J11", "Practitioner Clinic 1st Appointment Non Attendance (Patient)"
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I interrupt the subject's episode for "Redirect to Establish Attendance at Appointment"
    AdvanceFOBTScreeningEpisodePage(page).check_exception_circumstances_checkbox()
    AdvanceFOBTScreeningEpisodePage(
        page
    ).click_redirect_to_establish_attendance_at_appointment_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event code": "E183 Redirect to Establish Attendance at Appointment",
            "latest event status": "A25 1st Colonoscopy Assessment Appointment Booked, letter sent",
        },
    )

    # But there is no "J11" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment Non Attendance (Patient)"
    SubjectRepository().there_is_letter_batch_for_subject(
        nhs_no,
        "J11",
        "Practitioner Clinic 1st Appointment Non Attendance (Patient)",
        False,
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page=page).expand_episodes_list()
    SubjectScreeningSummaryPage(page=page).click_first_fobt_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "yesterday"
    AppointmentDetailPage(page).mark_appointment_as_attended(
        datetime.today() - timedelta(days=1)
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_number=nhs_no,
        criteria={
            "latest event status": "J10 Attended Colonoscopy Assessment Appointment",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        nhs_no=nhs_no, page=page
    )

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
    SubjectScreeningSummaryPage(page=page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(
        page=page
    ).click_suitable_for_endoscopic_test_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A99 Suitable for Endoscopic Test"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # And I enter a Diagnostic Test First Offered Appointment Date of "tomorrow"
    AdvanceFOBTScreeningEpisodePage(page).click_calendar_button()
    CalendarPicker(page).v1_calender_picker(datetime.today() + timedelta(days=1))

    # And I select Diagnostic Test Type "Colonoscopy"
    AdvanceFOBTScreeningEpisodePage(page).select_test_type_dropdown_option(
        "Colonoscopy"
    )

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
        nhs_number=nhs_no,
        criteria={
            "latest event status": "A259 Attended Diagnostic Test",
        },
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

    # And there is a clinician who meets the following criteria:
    user = User.from_user_role_type(user_role)
    query = PersonRepository().build_person_selection_query(
        criteria={
            "Person has current role": "Accredited Screening Colonoscopist",
            "Person has current role in organisation": "User's SC",
            "Resect & Discard accreditation status": "None",
        },
        person=None,
        required_person_count=1,
        user=user,
        subject=None,
    )
    df = OracleDB().execute_query(query=query, parameters=None)
    person_name = (
        f"{df["person_family_name"].iloc[0]} {df["person_given_name"].iloc[0]}"
    )

    # And I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_drug_information(
        {
            "drug_dose1": "3",
            "drug_type1": DrugTypeOptions.MANNITOL,
        }
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
            "comfort during examination": ComfortOptions.NO_DISCOMFORT,
            "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
            "endoscopist defined extent": EndoscopyLocationOptions.APPENDIX,
            "retroverted view": YesNoOptions.NO,
            "scope imager used": YesNoOptions.YES,
            "start of intubation time": "09:00",
            "start of extubation time": "09:30",
            "end time of procedure": "10:00",
            "scope id": "Autotest",
            "insufflation": InsufflationOptions.AIR,
            "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
            "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
        }
    )

    # I set the following completion proof values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_completion_information(
        {"completion proof": CompletionProofOptions.VIDEO_APPENDIX}
    )

    # I set the following failure reasons within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_failure_information(
        {"failure reasons": FailureReasonsOptions.NO_FAILURE_REASONS}
    )

    # I add new polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.ANASTOMOSIS,
            "classification": PolypClassificationOptions.IP,
            "polyp access": PolypAccessOptions.EASY,
            "estimate of whole polyp size": "11",
            "left in situ": YesNoOptions.NO,
        },
        1,
    )

    # I add interventions 1 for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "excised": YesNoOptions.YES,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "retrieved": PolypInterventionRetrievedOptions.YES,
        },
        1,
    )

    # I update histology details for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "date of reporting": datetime.today(),
            "date of receipt": datetime.today(),
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

    # I add new polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.CAECUM,
            "classification": PolypClassificationOptions.LST_NG,
            "polyp access": PolypAccessOptions.EASY,
            "estimate of whole polyp size": "5",
            "left in situ": YesNoOptions.NO,
        },
        2,
    )

    # I add interventions 1 for polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "excised": YesNoOptions.YES,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "retrieved": PolypInterventionRetrievedOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        },
        2,
    )

    # I update histology details for polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "date of reporting": datetime.today(),
            "date of receipt": datetime.today(),
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

    # I add new polyp 3 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.HEPATIC_FLEXURE,
            "classification": PolypClassificationOptions.LST_NG,
            "polyp access": PolypAccessOptions.EASY,
            "estimate of whole polyp size": "21",
            "left in situ": YesNoOptions.NO,
        },
        3,
    )

    # I add interventions 1 for polyp 3 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "excised": YesNoOptions.YES,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "retrieved": PolypInterventionRetrievedOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
            "polyp appears fully resected endoscopically": YesNoOptions.YES,
        },
        3,
    )

    # I update histology details for polyp 3 with the following fields and values within the Investigation Dataset for this subject:
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
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(
        polyp_number=1, expected_value="13"
    )

    # Then I confirm the Polyp Algorithm Size for Polyp 2 is 4
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(
        polyp_number=2, expected_value="4"
    )

    # Then I confirm the Polyp Algorithm Size for Polyp 3 is 21
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(
        polyp_number=3, expected_value="21"
    )

    # And I confirm the Polyp Category for Polyp 1 is "Advanced colorectal polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(
        polyp_number=1, expected_value="Advanced colorectal polyp"
    )

    # And I confirm the Polyp Category for Polyp 2 is "Premalignant polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(
        polyp_number=2, expected_value="Premalignant polyp"
    )

    # And I confirm the Polyp Category for Polyp 3 is "LNPCP"
    InvestigationDatasetsPage(page).assert_polyp_category(
        polyp_number=3, expected_value="LNPCP"
    )

    # And I confirm the Episode Result is "LNPCP"
    EpisodeRepository().confirm_episode_result(nhs_no, "LNPCP")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I select Outcome of Diagnostic Test "Refer Another Diagnostic Test"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_ANOTHER_DIAGNOSTIC_TEST
    )

    # And I select Radiological or Endoscopic Referral value "Endoscopic"
    DiagnosticTestOutcomePage(page).select_referral_procedure_type(
        ReferralProcedureType.ENDOSCOPIC
    )

    # And I select Reason for Onward Referral value "Multiple Polyps, not all Removed"
    DiagnosticTestOutcomePage(page).select_reason_for_onward_referral(
        ReasonForOnwardReferral.MULTIPLE_POLYPS_NOT_ALL_REMOVED
    )

    # And I set any onward referring clinician
    DiagnosticTestOutcomePage(page).select_valid_onward_referral_consultant_index(1)

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    criteria = {
        "which diagnostic test": "Latest not-void test in latest episode",
        "diagnostic test has outcome": "Refer Another Diagnostic Test",
        "diagnostic test has result": "LNPCP",
        "latest episode accumulated result": "LNPCP",
        "latest event status": "A315 Diagnostic Test Outcome Entered",
    }
    subject_assertion(nhs_no, criteria)

    # When I advance the subject's episode for "Post-investigation Appointment Required"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(
        page=page
    ).click_post_investigation_appointment_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A360 Post-investigation Appointment Required",
        },
    )

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
            "latest event status": "A410 Post-investigation Appointment Made",
        },
    )

    # And there is a "A410" letter batch for my subject with the exact title "Post-Investigation Appointment Invitation Letter"
    # When I process the open "A410" letter batch for my subject
    # Then my subject has been updated as follows:
    batch_processing(
        page,
        "A410",
        "Post-Investigation Appointment Invitation Letter",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A415 Post-investigation Appointment Invitation Letter Printed"
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(
        nhs_no=nhs_no, page=page
    )

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_fobt_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "today"
    AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A416 Post-investigation Appointment Attended",
        },
    )
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A316 Post-investigation Appointment Attended",
            "latest event status": "A430 Post-investigation Appointment Attended - Diagnostic Result Letter not Printed",
        },
    )

    # And there is a "A430" letter batch for my subject with the exact title "Result Letters Following Post-investigation Appointment"
    # When I process the open "A430" letter batch for my subject
    # Then my subject has been updated as follows:
    batch_processing(
        page,
        "A430",
        "Result Letters Following Post-investigation Appointment",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A395 Refer Another Diagnostic Test"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I select the advance episode option for "Record Contact with Patient"
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    AdvanceFOBTScreeningEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with values:
    ContactWithPatientPage(page).record_contact(
        "Close Episode with Existing result", "Yes"
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "A401 Patient Declined Follow-up Test"}
    )

    # And there is a "A401" letter batch for my subject with the exact title "Follow-up Test Cancelled by Patient"
    # When I process the open "A401" letter batch for my subject
    batch_processing(
        page,
        "A401",
        "Follow-up Test Cancelled by Patient",
    )

    # Then my subject has been updated as follows:
    criteria = {
        "which diagnostic test": "Latest not-void test in latest episode",
        "calculated fobt due date": "Unchanged",
        "calculated lynch due date": "Null",
        "calculated surveillance due date": "3 years from diagnostic test",
        "ceased confirmation date": "Null",
        "ceased confirmation details": "Null",
        "ceased confirmation user id": "Null",
        "clinical reason for cease": "Null",
        "latest episode accumulated result": "LNPCP",
        "latest episode recall calculation method": "Diagnostic test date",
        "latest episode recall episode type": "Surveillance - LNPCP",
        "latest episode recall surveillance type": "LNPCP",
        "latest episode status": "Closed",
        "latest episode status reason": "Episode Complete",
        "latest event status": "A157 LNPCP",
        "lynch due date": "Null",
        "lynch due date date of change": "Unchanged",
        "lynch due date reason": "Unchanged",
        "screening due date": "Null",
        "screening due date date of change": "Today",
        "screening due date reason": "Result referred to Surveillance",
        "screening status": "Surveillance",
        "screening status date of change": "Today",
        "screening status reason": "Result Referred to Surveillance",
        "surveillance due date": "Calculated Surveillance Due Date",
        "surveillance due date date of change": "Today",
        "surveillance due date reason": "Result - LNPCP",
        "symptomatic procedure date": "Null",
        "symptomatic procedure result": "Null",
        "screening referral type": "Null",
    }
    subject_assertion(nhs_no, criteria)

    LogoutPage(page).log_out()
