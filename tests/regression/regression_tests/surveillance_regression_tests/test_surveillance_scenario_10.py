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
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypInterventionModalityOptions,
    PolypInterventionRetrievedOptions,
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
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils import screening_subject_page_searcher
from utils.appointments import book_post_investigation_appointment
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
def test_scenario_10(page: Page, general_properties: dict) -> None:
    """
    Scenario: 10: High-risk result from diagnostic test (over-age)

    X500-X505-A99-A59-A259-A315-A360-A410-A415-A416-A316-A430-A158-X394-X391-X372-X374-C203 [SSCL25c]

    This scenario tests a straight pathway for an over-age subject through a Surveillance episode from invitation to closure, where one diagnostic test took place giving a High-risk findings result.  It also checks that in a Surveillance episode the first test need not necessarily be a full Colonoscopy - and that if the actual extent recorded is "beyond" the intended extent, this can change the type of test.  The subject is discharged from Surveillance for age.

    Scenario summary:

    > Run surveillance invitations for 1 subject > X500 (3.1)
    > SSPI update changes subject to over-age at recall
    > Process X500 letter batch > X505 (3.1)
    > Complete the colonoscopy assessment dataset - fit for colonoscopy
    > Record patient contact – contacted, suitable for colonoscopy > A99 (3.1)
    > Invite for diagnostic test > A59 (2.1)
    > Attend diagnostic test > A259 (2.1)
    > Complete investigation dataset – High-risk findings (2.1)
    > Enter diagnostic test outcome – investigation complete > A315 (2.1)
    > Post-investigation appointment required > A360 (2.1)
    > Book post-investigation appointment > A410 (2.4)
    > Process A410 letter batch > A415 (2.4)
    > Attend post-investigation appointment > A416 > A316 > A430 (2.4)
    > Process A430 letter batch > A158 (2.4) > X394 (3.5)
    > Handover to clinician > X391 (3.6)
    > Process X391 letter batch > X372 (3.6)
    > Process X372 letter batch > X374 > C203 (3.6)
    > Check recall [SSCL25c]
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

    # And I receive an SSPI update to change their date of birth to "87" years old
    SSPIChangeSteps().sspi_update_to_change_dob_received(nhs_no, 87)

    # Then my subject has been updated as follows:
    subject_assertion(nhs_no, {"subject age": "87"})

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

    # And I select Diagnostic Test Type "Flexible Sigmoidoscopy"
    AdvanceSurveillanceEpisodePage(page).select_test_type_dropdown_option(
        "Flexible Sigmoidoscopy"
    )

    # And I select Intended Extent "Descending Colon"
    AdvanceSurveillanceEpisodePage(page).select_intended_extent_dropdown_option(
        "Descending Colon"
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

    # Then I confirm the "Investigation Dataset" section of the dataset contains the field "Actual Type of Test" with the value of "Flexible Sigmoidoscopy"
    InvestigationDatasetsPage(page).does_field_contain_expected_value(
        "Investigation Dataset", None, "Actual Type of Test", "Flexible Sigmoidoscopy"
    )

    # Then I get a confirmation prompt that "contains" "Are you sure you want to change the actual type of diagnostic test to Colonoscopy?"
    # When I press OK on my confirmation prompt
    InvestigationDatasetsPage(page).assert_dialog_text(
        "Are you sure you want to change the actual type of diagnostic test to Colonoscopy?",
        True,
    )

    # When I set the following fields and values within the Investigation Dataset for this subject:
    InvestigationDatasetsPage(page).click_show_endoscopy_information()
    DatasetFieldUtil(page).populate_select_locator_for_field(
        "Endoscopist defined extent", EndoscopyLocationOptions.APPENDIX
    )

    # Then I confirm the "Investigation Dataset" section of the dataset contains the field "Actual Type of Test" with the value of "Colonoscopy"
    InvestigationDatasetsPage(page).does_field_contain_expected_value(
        "Investigation Dataset", None, "Actual Type of Test", "Colonoscopy"
    )

    # When I add the following bowel preparation drugs and values within the Investigation Dataset for this subject:
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

    # And I set the following completion proof values within the Investigation Dataset for this subject:
    completion_information = {"completion proof": CompletionProofOptions.VIDEO_APPENDIX}

    # And I set the following failure reasons within the Investigation Dataset for this subject:
    failure_information = {"failure reasons": FailureReasonsOptions.NO_FAILURE_REASONS}

    # And I add new polyps 1-2 with the following fields and values within the Investigation Dataset for this subject:
    polyp_information = [
        {
            "location": EndoscopyLocationOptions.CAECUM,
            "classification": PolypClassificationOptions.LST_NG,
            "estimate of whole polyp size": "10",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
        {
            "location": EndoscopyLocationOptions.ASCENDING_COLON,
            "classification": PolypClassificationOptions.IIA,
            "estimate of whole polyp size": "12",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        },
    ]

    # And I add intervention 1 for polyps 1-2 with the following fields and values within the Investigation Dataset for this subject:
    polyp_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.EMR,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.YES,
                "retrieved": PolypInterventionRetrievedOptions.NO,
                "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
            }
        ],
        [
            {
                "modality": PolypInterventionModalityOptions.POLYPECTOMY,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.YES,
                "retrieved": PolypInterventionRetrievedOptions.NO,
                "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
                "polyp appears fully resected endoscopically": YesNoUncertainOptions.UNCERTAIN,
            }
        ],
    ]

    # And I mark the Investigation Dataset as completed
    # When I press the save Investigation Dataset button
    InvestigationDatasetsPage(page).click_show_endoscopy_information()
    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        endoscopy_information=endoscopy_information,
        drug_information=drug_information,
        general_information=general_information,
        failure_information=failure_information,
        completion_information=completion_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
    )

    # Then the Investigation Dataset result message is "High-risk findings"
    InvestigationDatasetsPage(page).assert_test_result("High-risk findings")

    # Then I confirm the Polyp Algorithm Size for Polyp 1 is 10
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(1, "10")

    # And I confirm the Polyp Algorithm Size for Polyp 2 is 12
    InvestigationDatasetsPage(page).assert_polyp_algorithm_size(2, "12")

    # And I confirm the Polyp Category for Polyp 1 is "Advanced colorectal polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(
        1, "Advanced colorectal polyp"
    )

    # And I confirm the Polyp Category for Polyp 2 is "Advanced colorectal polyp"
    InvestigationDatasetsPage(page).assert_polyp_category(
        2, "Advanced colorectal polyp"
    )

    # And my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest episode accumulated result": "High-risk findings"},
    )

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
        OutcomeOfDiagnosticTest.REFER_SURVEILLANCE
    )

    # And I save the Diagnostic Test Outcome
    DiagnosticTestOutcomePage(page).click_save_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A315 Diagnostic Test Outcome Entered"},
    )

    # When I advance the subject's episode for "Post-investigation Appointment Required"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(
        page
    ).click_post_investigation_appointment_required_button()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {"latest event status": "A360 Post-investigation Appointment Required"},
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
        {
            "latest episode includes event status": "A416 Post-investigation Appointment Attended"
        },
    )

    # And my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A316 Post-investigation Appointment Attended",
        },
    )

    # And my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest episode includes event status": "A158 High-risk findings",
            "latest event status": "X394 Handover into Symptomatic Care - Patient Age",
        },
    )

    # When I view the subject
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)

    # And I select the advance episode option for "Initiate Close"
    SubjectScreeningSummaryPage(page).click_advance_surveillance_episode_button()
    AdvanceSurveillanceEpisodePage(page).click_initiate_close_button()

    # And I fill in Handover into Symptomatic Care form with Referral to Specific Clinician
    HandoverIntoSymptomaticCarePage(
        page
    ).perform_referral_to_specific_clinician_scenario()

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no, {"latest event status": "X391 Handover into Symptomatic Care"}
    )

    # And there is a "X391" letter batch for my subject with the exact title "Handover into Symptomatic Care - Age (GP Letter)"
    # And I process the open "X391" letter batch for my subject
    batch_processing(
        page,
        "X391",
        "Handover into Symptomatic Care - Age (GP Letter)",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "X372 Handover into Symptomatic Care - GP Letter Printed"
        },
    )

    # And there is a "X372" letter batch for my subject with the exact title "Handover into Symptomatic Care Adenoma Surveillance - Patient Letter"
    # And I process the open "X372" letter batch for my subject
    batch_processing(
        page,
        "X372",
        "Handover into Symptomatic Care Adenoma Surveillance - Patient Letter",
    )

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "which diagnostic test": "Only not-void test in latest episode",
            "calculated fobt due date": "2 years from diagnostic test",
            "calculated lynch due date": "Null",
            "calculated surveillance due date": "Null",
            "ceased confirmation date": "Today",
            "ceased confirmation details": "Handover notes - referral to Specific Clinician",
            "ceased confirmation user id": "User's ID",
            "clinical reason for cease": "Null",
            "latest episode includes event status": "A158 High-risk findings",
            "latest episode recall calculation method": "Diagnostic test date",
            "latest episode recall episode type": "Surveillance - High-risk findings",
            "latest episode recall surveillance type": "Null",
            "latest episode status": "Closed",
            "latest episode status reason": "Discharge from Surveillance - Age",
            "latest event status": "X374 Handover into Symptomatic Care - Patient Letter Printed",
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
            "symptomatic procedure date": "Null",
            "symptomatic procedure result": "Null",
            "screening referral type": "Null",
        },
        user_role,
    )

    LogoutPage(page).log_out()
