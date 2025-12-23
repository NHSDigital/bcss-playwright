import logging
from datetime import datetime
import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.datasets.colonoscopy_dataset_page import (
    ColonoscopyDatasetsPage,
    FitForColonoscopySspOptions,
)
from pages.datasets.investigation_dataset_page import (
    AdenomaSubTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    CompletionProofOptions,
    DrugTypeOptions,
    EndoscopyLocationOptions,
    FailureReasonsOptions,
    InsufflationOptions,
    InvestigationDatasetsPage,
    LateOutcomeOptions,
    OutcomeAtTimeOfProcedureOptions,
    PolypAccessOptions,
    PolypClassificationOptions,
    PolypDysplasiaOptions,
    PolypExcisionCompleteOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypInterventionModalityOptions,
    PolypInterventionRetrievedOptions,
    PolypTypeOptions,
    YesNoOptions,
    YesNoUncertainOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
from pages.organisations.organisations_page import OrganisationSwitchPage
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
)
from pages.screening_subject_search.advance_surveillance_episode_page import (
    AdvanceSurveillanceEpisodePage,
)
from pages.screening_subject_search.attend_diagnostic_test_page import (
    AttendDiagnosticTestPage,
)
from pages.screening_subject_search.contact_with_patient_page import (
    ContactWithPatientPage,
)
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_subject_search.handover_into_symptomatic_care_page import (
    HandoverIntoSymptomaticCarePage,
)
from pages.screening_subject_search.reopen_surveillance_episode_page import (
    ReopenSurveillanceEpisodePage,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.appointments import book_post_investigation_appointment
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.sspi_change_steps import SSPIChangeSteps
from utils.subject_assertion import subject_assertion
from utils.subject_demographics import SubjectDemographicUtil
from utils.user_tools import UserTools


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_scenario_13(page: Page, general_properties: dict) -> None:
    """
    Scenario: 13: Cancer from diagnostic tests

    X501-A99-A59-A259-A360-A410-A415-A416-A316-A345-A346-A63-C203 [SSCL18c] A416-A316-A345-A346-A63-X399-C203 [SSCL25a]

    This scenario takes an in-age Surveillance episode through to closure on Cancer result from diagnostic tests, returning the subject to FOBT screening.  The diagnostic test outcome is only entered after the post-investigation appointment has been attended (and cannot be entered until the investigation dataset has been completed).  The episode is then reopened and the subject’s date of birth changed in order to test closure on the same result for an over-age subject.  This reopen is not available to an SSP, after closure on Cancer result, but is available to a Screening Centre Manager.

    Because we cannot know if we will be inviting a subject who has had previous FOBT episodes, or only a bowel scope episode, it is impossible to check if they will be set to Call or Recall; we can only check that they are not longer in Surveillance status.

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to in-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Record patient contact – contacted, suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – Cancer (2.1)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 (2.4)
    > Enter diagnostic test outcome – refer MDT > A316 (2.4) > A345 (2.6)
    > Handover into symptomatic care > A346 (2.7)
    > Process A346 letter batch > A63 (2.7) > C203 (3.6)
    > Check recall [SSCL18c]
    > Reopen to confirm diagnostic test result and outcome > A416 (2.4)
    > Manually change subject to over age
    > Enter diagnostic test outcome – refer MDT > A316 (2.4) > A345 (2.6)
    > Handover into symptomatic care > A346 (2.7)
    > Process A346 letter batch > A63 (2.7) > X399 (3.5) > C203 (3.6)
    > Check recall [SSCL25a]
    """
    # Given I log in to BCSS "England" as user role "Specialist Screening Practitioner"
    user_role = UserTools.user_login(
        page, "Specialist Screening Practitioner at BCS009 & BCS001", True
    )

    OrganisationSwitchPage(page).select_organisation_by_id("BCS001")
    OrganisationSwitchPage(page).click_continue()
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

    # And I receive an SSPI update to change their date of birth to "72" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 72)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "72"})

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

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the advance episode options
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

    # When I select the advance episode option for "Attend Diagnostic Test"
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

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # Confirm on the investigation Datasets Page
    InvestigationDatasetsPage(page).bowel_cancer_screening_page_title_contains_text(
        "Investigation Datasets"
    )

    # And I open all minimized sections on the dataset
    InvestigationDatasetsPage(page).open_all_minimized_sections()

    # And I apply the "CancerDetected2" Investigation Dataset Scenario
    # When I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_drug_information(
        {
            "drug_dose1": "10",
            "drug_type1": DrugTypeOptions.BISACODYL,
            "drug_dose2": "20",
            "drug_type2": DrugTypeOptions.CITRAFLEET,
        }
    )

    # And I set the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_general_information(
        {
            "practitioner": 1,
            "site": 1,
            "testing clinician": 1,
            "aspirant endoscopist": 1,
        }
    )

    InvestigationDatasetCompletion(page).fill_endoscopy_information(
        {
            "endoscope inserted": "yes",
            "procedure type": "therapeutic",
            "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
            "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
            "comfort during examination": ComfortOptions.NO_DISCOMFORT,
            "endoscopist defined extent": EndoscopyLocationOptions.ANASTOMOSIS,
            "scope imager used": YesNoOptions.YES,
            "retroverted view": YesNoOptions.YES,
            "start of intubation time": "09:00",
            "start of extubation time": "09:15",
            "end time of procedure": "09:30",
            "scope id": "A1",
            "insufflation": InsufflationOptions.AIR,
            "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
            "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
        }
    )

    # And I set the following completion proof values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_completion_information(
        {"completion proof": CompletionProofOptions.VIDEO_ANASTOMOSIS}
    )

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_out_failure_information(
        {"failure reasons": FailureReasonsOptions.NO_FAILURE_REASONS}
    )

    # And I add new polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_information(
        {
            "location": EndoscopyLocationOptions.RECTUM,
            "classification": PolypClassificationOptions.IIA,
            "estimate of whole polyp size": "10",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        1,
    )

    # And I add intervention 1 for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": PolypInterventionRetrievedOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        },
        1,
    )

    # And I update histology details for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": -1,
            "pathologist": -1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.NOT_REPORTED,
            "polyp excision complete": PolypExcisionCompleteOptions.R0,
            "polyp size": "5",
            "polyp dysplasia": PolypDysplasiaOptions.NOT_REPORTED,
            "polyp carcinoma": YesNoUncertainOptions.YES,
        },
        1,
    )

    # When I press the save Investigation Dataset button
    InvestigationDatasetsPage(page).click_save_dataset_button()

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest episode accumulated result": "Null"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Post-investigation Appointment Required"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_post_investigation_appointment_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "A360 Post-investigation Appointment Required"}
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
            "latest event status": "A410 Post-investigation Appointment Made",
        },
    )

    # And there is a "A410" letter batch for my subject with the exact title "Post-Investigation Appointment Invitation Letter"
    # When I process the open "A410" letter batch for my subject
    batch_processing(
        page,
        "A410",
        "Post-Investigation Appointment Invitation Letter",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A415 Post-investigation Appointment Invitation Letter Printed",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I view the event history for the subject's latest episode
    SubjectScreeningSummaryPage(page).expand_episodes_list()
    SubjectScreeningSummaryPage(page).click_first_surveillance_episode_link()

    # And I view the latest practitioner appointment in the subject's episode
    EpisodeEventsAndNotesPage(page).click_most_recent_view_appointment_link()

    # And I attend the subject's practitioner appointment "today"
    AppointmentDetailPage(page).mark_appointment_as_attended(datetime.today())

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A416 Post-investigation Appointment Attended"},
    )

    # Then I get a confirmation prompt that "contains" "It is not possible to progress this episode until the dataset has been marked as complete and a diagnostic test result written to the episode history."
    AdvanceSurveillanceEpisodePage(page).assert_dialog_text(
        "It is not possible to progress this episode until the dataset has been marked as complete and a diagnostic test result written to the episode history.",
        True,
    )

    # When I select the advance episode option for "Enter Diagnostic Test Outcome"
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I edit the Investigation Dataset for this subject
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    # Confirm on the investigation Datasets Page
    InvestigationDatasetsPage(page).bowel_cancer_screening_page_title_contains_text(
        "Investigation Datasets"
    )

    InvestigationDatasetsPage(page).click_edit_dataset_button()

    # And I open all minimized sections on the dataset
    InvestigationDatasetsPage(page).open_all_minimized_sections()

    # And I mark the Investigation Dataset as completed
    InvestigationDatasetsPage(page).check_dataset_complete_checkbox()

    # When I press the save Investigation Dataset button
    # Then the Investigation Dataset result message, which I will cancel, is "Cancer Detected"
    InvestigationDatasetsPage(page).click_save_dataset_button_assert_dialog(
        "Cancer Detected"
    )

    # When I press the save Investigation Dataset button
    InvestigationDatasetsPage(page).click_save_dataset_button()

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"latest episode accumulated result": "Cancer Detected"})

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I select Outcome of Diagnostic Test "Refer MDT"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_MDT
    )

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A316 Post-investigation Appointment Attended",
            "latest event status": "A345 Cancer Result, Refer MDT",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select the advance episode option for "Handover into Symptomatic Care"
    AdvanceSurveillanceEpisodePage(page).click_handover_into_symptomatic_care_button()

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
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "diagnostic test has outcome": "Yes",
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
            "screening due date": "Calculated FOBT Due Date",
            "screening due date date of change": "Today",
            "screening due date reason": "Result referred for cancer treatment",
            "screening status": "NOT: Surveillance",
            "screening status date of change": "Today",
            "screening status reason": "Result referred for cancer treatment",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Referred for Cancer treatment",
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Null",
            "screening referral type": "Null",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # Then I "cannot" reopen the subject's episode
    SubjectScreeningSummaryPage(page).assert_reopen_episode_button_not_visible()

    # When I switch users to BCSS "England" as user role "Screening Centre Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    user_role = UserTools.user_login(page, "Screening Centre Manager at BCS001", True)
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # And I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I reopen the subject's episode for "Reopen to Confirm Diagnostic Test Result and Outcome"
    SubjectScreeningSummaryPage(page).click_reopen_surveillance_episode_button()
    ReopenSurveillanceEpisodePage(
        page
    ).click_reopen_to_confirm_diagnostic_test_result_and_outcome_button()

    # And I pause for "2" seconds to let the process complete
    page.wait_for_timeout(2000)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Latest not-void test in latest episode",
            "calculated fobt due date": "Null",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "As at episode start",
            "ceased confirmation date": "Null",
            "ceased confirmation details": "Null",
            "ceased confirmation user id": "Null",
            "clinical reason for cease": "Null",
            "diagnostic test has outcome": "No",
            "latest episode accumulated result": "Cancer Detected",
            "latest episode includes event code": "E67 Reopen to Confirm Diagnostic Test Result and Outcome",
            "latest episode recall calculation method": "Null",
            "latest episode recall episode type": "Null",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Open",
            "latest episode status reason": "Null",
            "latest event status": "A416 Post-investigation Appointment Attended",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Today",
            "screening due date reason": "Reopened episode",
            "screening status": "Surveillance",
            "screening status date of change": "Today",
            "screening status reason": "Reopened episode",
            "surveillance due date": "Calculated Surveillance due date",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Reopened episode",
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Null",
            "screening referral type": "Null",
        },
    )

    # When I view the subject
    # And I update the subject's date of birth to make them 85 years old
    # And I update the subject's postcode to "AA1 2BB"
    # And I save my changes to the subject's demographics
    SubjectDemographicUtil(page).updated_subject_demographics(
        nhs_no,
        85,
        "AA1 2BB",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "subject age": "85",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # And I select Outcome of Diagnostic Test "Refer MDT"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_MDT
    )

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A316 Post-investigation Appointment Attended",
            "latest event status": "A345 Cancer Result, Refer MDT",
        },
    )

    # When I view the advance episode options
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()

    # And I select the advance episode option for "Handover into Symptomatic Care"
    AdvanceSurveillanceEpisodePage(page).click_handover_into_symptomatic_care_button()

    # And I fill in Handover into Symptomatic Care with Cancer details
    HandoverIntoSymptomaticCarePage(page).fill_with_cancer_details()

    # And my subject has been updated as follows:
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
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "Handover notes for Cancer scenario",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "diagnostic test has outcome": "Yes",
            "latest episode accumulated result": "Cancer Detected",
            "latest episode includes event status": "A63 Cancer",
            "latest episode recall calculation method": "Episode end date",
            "latest episode recall episode type": "FOBT Screening",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Discharge from Surveillance - Age",
            "latest event status": "X399 Discharged  from Surveillance - National Guidelines Cease Screening",
            "lynch due date": "Null",
            "lynch due date date of change": "Unchanged",
            "lynch due date reason": "Unchanged",
            "screening due date": "Null",
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Ceased",
            "screening status date of change": "Today",
            "screening status reason": "Outside screening population",
            "surveillance due date": "Null",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Discharge from Surveillance - Age",
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Null",
            "screening referral type": "Null",
        },
        user_role,
    )

    LogoutPage(page).log_out()
