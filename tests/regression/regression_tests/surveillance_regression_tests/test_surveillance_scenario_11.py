import logging
from datetime import datetime
import pytest
from playwright.sync_api import Page

from classes.repositories.person_repository import PersonRepository
from classes.user.user import User
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
    ReasonPathologyLostOptions,
    YesNoOptions,
    YesNoUncertainOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
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
    ReasonForOnwardReferral,
    ReferralProcedureType,
)
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.calendar_picker import CalendarPicker
from utils.dataset_field_util import DatasetFieldUtil
from utils.generate_health_check_forms_util import GenerateHealthCheckFormsUtil
from utils.investigation_dataset import InvestigationDatasetCompletion
from utils.oracle.oracle import OracleDB
from utils.sspi_change_steps import SSPIChangeSteps
from utils.subject_assertion import subject_assertion
from utils.user_tools import UserTools


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.surveillance_regression_tests
def test_surveillance_scenario_11(page: Page, general_properties: dict) -> None:
    """
    Scenario: 11: Close on existing LNPCP result

    X500-X505-A99-A59-A259-A315-A361-A323-A317-A318-A395-A99-A59-A306-A400-A157-C203 [SSCL52b]

    This scenario tests where a subject has had one diagnostic test and been referred for a second, which is cancelled.  Then contact with the subject is lost and the episode is closed on the existing result of LNPCP.  Below age at recall, the subject remains in Surveillance.

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to below-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Record patient contact – contacted, suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – LNPCP (2.1)
    > Enter diagnostic test outcome – refer another test > A315 (2.1)
    > Post-investigation appointment not required > A361 (2.1)
    > Record patient contact – post-investigation appointment not required > A323 (2.1) > A317 > A318 (2.5)
    > Process A318 letter batch > A395 (2.5)
    > Record patient contact – suitable for colonoscopy > A99 (2.3)
    > Invite for diagnostic test > A59 (2.1)
    > Cancel diagnostic test > A306 (2.1)
    > Record patient contact – not contacted, close on existing result > A400 (2.2)
    > Process A400 letter batch > A157 (2.2) > C203 (3.6)
    > Check recall [SSCL52b]
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

    # And I receive an SSPI update to change their date of birth to "44" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 44)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "44"})

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

    # And I select Diagnostic Test Type "Limited Colonoscopy"
    AdvanceSurveillanceEpisodePage(page).select_test_type_dropdown_option(
        "Limited Colonoscopy"
    )

    # And I select Intended Extent "Ascending Colon"
    AdvanceSurveillanceEpisodePage(page).select_intended_extent_dropdown_option(
        "Ascending Colon"
    )

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

    # Then I get a confirmation prompt that "contains" "The Endoscopist Defined Extent selected indicates that the diagnostic test type is Colonoscopy."
    # When I press OK on my confirmation prompt
    InvestigationDatasetsPage(page).assert_dialog_text(
        "The Endoscopist Defined Extent selected indicates that the diagnostic test type is Colonoscopy.",
        True,
    )

    # When I set the following fields and values within the Investigation Dataset for this subject:
    DatasetFieldUtil(page).populate_select_locator_for_field(
        "Endoscopist defined extent", EndoscopyLocationOptions.CAECUM
    )

    # Then I confirm the "Investigation Dataset" section of the dataset contains the field "Actual Type of Test" with the value of "Colonoscopy"
    DatasetFieldUtil(page).assert_cell_to_right_has_expected_text(
        "Actual Type of Test", "Colonoscopy"
    )

    # When I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
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
            "location": EndoscopyLocationOptions.SPLENIC_FLEXURE,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "11",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        1,
    )

    # And I add intervention 1 for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_intervention(
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": PolypInterventionRetrievedOptions.YES,
        },
        1,
    )

    # And I update histology details for polyp 1 with the following fields and values within the Investigation Dataset for this subject:
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

    # And I add intervention 1 for polyp 2 with the following fields and values within the Investigation Dataset for this subject:
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

    # And I update histology details for polyp 2 with the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetCompletion(page).fill_polyp_x_histology(
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": 1,
            "pathologist": 1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.TUBULAR_ADENOMA,
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

    # And I add intervention 1 for polyp 3 with the following fields and values within the Investigation Dataset for this subject:
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

    # And I update histology details for polyp 3 with the following fields and values within the Investigation Dataset for this subject:
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

    # And I confirm the Polyp Algorithm Size for Polyp 2 is 4
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(2, "4")

    # And I confirm the Polyp Algorithm Size for Polyp 3 is 21
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(3, "21")

    # And I confirm the Polyp Category for Polyp 1 is "Advanced colorectal polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(
        1, "Advanced colorectal polyp"
    )

    # And I confirm the Polyp Category for Polyp 2 is "Premalignant polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(2, "Premalignant polyp")

    # And I confirm the Polyp Category for Polyp 3 is "LNPCP"
    InvestigationDatasetsPage(page).assert_polyp_category(3, "LNPCP")

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Enter Diagnostic Test Outcome"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_enter_diagnostic_test_outcome_button()

    # Then I confirm the Outcome Of Diagnostic Test dropdown has the following options:
    DiagnosticTestOutcomePage(page).test_outcome_dropdown_contains_options(
        [
            "Refer Another Diagnostic Test",
            "Refer Symptomatic",
            "Refer Surveillance (BCSP)",
        ],
    )

    # When I select Outcome of Diagnostic Test "Refer Surveillance (BCSP)"
    DiagnosticTestOutcomePage(page).select_test_outcome_option(
        OutcomeOfDiagnosticTest.REFER_ANOTHER_DIAGNOSTIC_TEST
    )

    # And I select Radiological or Endoscopic Referral value "Endoscopic"
    DiagnosticTestOutcomePage(page).select_referral_procedure_type(
        ReferralProcedureType.ENDOSCOPIC
    )

    # Then I confirm the Reason for Onward Referral dropdown has the following options:
    DiagnosticTestOutcomePage(
        page
    ).reason_for_onward_referral_dropdown_contains_options(
        [
            "Polyp not Fully Excised",
            "Check Polyp Site",
            "Multiple Polyps, not all Removed",
            "Histology Required",
            "Unexplained Symptoms",
            "Interventions Required",
            "Incomplete Colonic Visualisation",
        ]
    )

    # And I select Reason for Onward Referral value "Check Polyp Site"
    DiagnosticTestOutcomePage(page).select_reason_for_onward_referral(
        ReasonForOnwardReferral.CHECK_POLYP_SITE
    )

    # And I set any onward referring clinician
    DiagnosticTestOutcomePage(page).select_valid_onward_referral_consultant_index(1)

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A315 Diagnostic Test Outcome Entered"},
    )

    # When I advance the subject's episode for "Other Post-investigation Contact Required"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_other_post_investigation_contact_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A361 Other Post-investigation Contact Required"},
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Record other post-investigation contact"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_record_other_post_investigation_contact_button()

    # And I confirm the patient outcome dropdown has the following options:
    ContactWithPatientPage(page).outcome_dropdown_contains_options(
        [
            "Post-investigation Appointment Not Required",
            "Post-investigation Appointment Required",
            "No outcome",
        ]
    )

    # And I record contact with the subject with outcome "Post-investigation Appointment Not Required"
    ContactWithPatientPage(page).record_post_investigation_appointment_not_required()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "A318 Post-investigation Appointment NOT Required - Result Letter Created"
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
        nhs_no, {"latest event status": "A395 Refer Another Diagnostic Test"}
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # When I select the advance episode option for "Record Contact with Patient"
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

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I advance the subject's episode for "Cancel Diagnostic Test"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_cancel_diagnostic_test_button()

    # Then my subject has been updated as follows:
    AdvanceSurveillanceEpisodePage(page).verify_latest_event_status_value(
        "A306 - Cancel Diagnostic Test"
    )

    # And I select the advance episode option for "Record Contact with Patient"
    AdvanceSurveillanceEpisodePage(page).click_record_contact_with_patient_button()

    # And I record contact with the subject with values:
    ContactWithPatientPage(page).record_contact(
        "Close Episode with Existing result", "No"
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A400 Follow-up Test Cancelled by Screening Centre"},
    )

    # And there is a "A400" letter batch for my subject with the exact title "Follow-up Test Cancelled by Screening Centre"
    # When I process the open "A400" letter batch for my subject
    batch_processing(
        page,
        "A400",
        "Follow-up Test Cancelled by Screening Centre",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
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
            "screening due date date of change": "Unchanged",
            "screening due date reason": "Unchanged",
            "screening status": "Surveillance",
            "screening status date of change": "Unchanged",
            "screening status reason": "Unchanged",
            "surveillance due date": "Calculated Surveillance due date",
            "surveillance due date date of change": "Today",
            "surveillance due date reason": "Result - LNPCP",
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Null",
            "screening referral type": "Null",
        },
    )

    LogoutPage(page).log_out()
