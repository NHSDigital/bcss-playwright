# Create a new util that can populate the investigations dataset to get the following
# results:

# High risk
# LNPCP
# Normal

# This needs to be done as there is a lot of repeat code between the three results
# and we need 2 subjects with high risk and LNPCP results.
# Also create any utils to reduce the amount of duplicated code
# to as close to 0% as possible.

# Update compartment 6

# Add utility guide

# In the code I have added these comments to show the different actions:
# This needs to be repeated for 1 subject, age does not matter - Normal Result
# This needs to be repeated for two subjects, one old and one not - LNPCP Result
# This needs to be repeated for two subjects, one old and one not - High Risk Result

from playwright.sync_api import Page
from enum import StrEnum
import logging
from pages.base_page import BasePage
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.screening_subject_search.handover_into_symptomatic_care_page import (
    HandoverIntoSymptomaticCarePage,
)
from utils.calendar_picker import CalendarPicker
from datetime import datetime
from pages.screening_subject_search.diagnostic_test_outcome_page import (
    DiagnosticTestOutcomePage,
    OutcomeOfDiagnosticTest,
)
from pages.datasets.investigation_dataset_page import (
    InvestigationDatasetsPage,
    SiteLookupOptions,
    PractitionerOptions,
    TestingClinicianOptions,
    AspirantEndoscopistOptions,
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    YesNoOptions,
    InsufflationOptions,
    OutcomeAtTimeOfProcedureOptions,
    LateOutcomeOptions,
    CompletionProofOptions,
    FailureReasonsOptions,
    PolypClassificationOptions,
    PolypAccessOptions,
    PolypInterventionModalityOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
)
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisodePage,
)
from utils.dataset_field_util import DatasetFieldUtil
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)


class InvestigationDatasetResults(StrEnum):
    """
    Enum containing the different investigation dataset results.
    This is stored here to result the risk of typo's when calling the methods.
    """

    HIGH_RISK = "High Risk"
    LNPCP = "LNPCP"
    NORMAL = "Normal"


class InvestigationDatasetCompletion:
    def __init__(self, page: Page):
        self.page = page
        self.estimate_whole_polyp_size_string = "Estimate of whole polyp size"
        self.polyp_access_string = "Polyp Access"

    def complete_with_result(self, nhs_no: str, result: str):
        if result == InvestigationDatasetResults.HIGH_RISK:
            self.go_to_investigation_datasets_page(nhs_no)
            self.default_investigation_dataset_forms()
            InvestigationDatasetsPage(self.page).select_therapeutic_procedure_type()
            self.default_investigation_dataset_forms_continuation()
            self.investigation_datasets_failure_reason()
            self.polyps_for_high_risk_result()
            self.save_investigation_dataset()
        elif result == InvestigationDatasetResults.LNPCP:
            self.go_to_investigation_datasets_page(nhs_no)
            self.default_investigation_dataset_forms()
            InvestigationDatasetsPage(self.page).select_therapeutic_procedure_type()
            self.default_investigation_dataset_forms_continuation()
            self.investigation_datasets_failure_reason()
            self.polyps_for_lnpcp_result()
            self.save_investigation_dataset()
        elif result == InvestigationDatasetResults.NORMAL:
            self.go_to_investigation_datasets_page(nhs_no)
            self.default_investigation_dataset_forms()
            InvestigationDatasetsPage(self.page).select_diagnostic_procedure_type()
            self.default_investigation_dataset_forms_continuation()
            InvestigationDatasetsPage(self.page).click_show_failure_information()
            DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
                "Failure Reasons",
                "divFailureSection",
                FailureReasonsOptions.NO_FAILURE_REASONS,
            )
            self.save_investigation_dataset()
        else:
            logging.error("Incorrect result entered")

    def go_to_investigation_datasets_page(self, nhs_no) -> None:
        verify_subject_event_status_by_nhs_no(
            self.page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
        )

        SubjectScreeningSummaryPage(self.page).click_datasets_link()
        SubjectDatasetsPage(self.page).click_investigation_show_datasets()

    def default_investigation_dataset_forms(self) -> None:
        # Investigation Dataset
        InvestigationDatasetsPage(self.page).select_site_lookup_option(
            SiteLookupOptions.RL401
        )
        InvestigationDatasetsPage(self.page).select_practitioner_option(
            PractitionerOptions.AMID_SNORING
        )
        InvestigationDatasetsPage(self.page).select_testing_clinician_option(
            TestingClinicianOptions.BORROWING_PROPERTY
        )
        InvestigationDatasetsPage(self.page).select_aspirant_endoscopist_option(
            AspirantEndoscopistOptions.ITALICISE_AMNESTY
        )
        # Drug Information
        InvestigationDatasetsPage(self.page).click_show_drug_information()
        InvestigationDatasetsPage(self.page).select_drug_type_option1(
            DrugTypeOptions.BISACODYL
        )
        InvestigationDatasetsPage(self.page).fill_drug_type_dose1("10")
        # Ensocopy Information
        InvestigationDatasetsPage(self.page).click_show_endoscopy_information()
        InvestigationDatasetsPage(self.page).check_endoscope_inserted_yes()

    def default_investigation_dataset_forms_continuation(self) -> None:
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Bowel preparation quality", BowelPreparationQualityOptions.GOOD
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Comfort during examination", ComfortOptions.NO_DISCOMFORT
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Comfort during recovery", ComfortOptions.NO_DISCOMFORT
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Endoscopist defined extent", EndoscopyLocationOptions.ILEUM
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Scope imager used", YesNoOptions.YES
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Retroverted view", YesNoOptions.NO
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field(
            "Start of intubation time", "09:00"
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field(
            "Start of extubation time", "09:15"
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field(
            "End time of procedure", "09:30"
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field("Scope ID", "A1")
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Insufflation", InsufflationOptions.AIR
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Outcome at time of procedure",
            OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Late outcome", LateOutcomeOptions.NO_COMPLICATIONS
        )
        InvestigationDatasetsPage(self.page).click_show_completion_proof_information()
        # Completion Proof Information
        DatasetFieldUtil(self.page).populate_select_locator_for_field(
            "Proof Parameters", CompletionProofOptions.PHOTO_ILEO
        )

    def investigation_datasets_failure_reason(self) -> None:
        # Failure Information
        InvestigationDatasetsPage(self.page).click_show_failure_information()
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Failure Reasons",
            "divFailureSection",
            FailureReasonsOptions.BLEEDING_INCIDENT,
        )

    def polyps_for_high_risk_result(self) -> None:
        # Polyp Information
        InvestigationDatasetsPage(self.page).click_add_polyp_button()
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Location", "divPolypNumber1Section", EndoscopyLocationOptions.ILEUM
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Classification", "divPolypNumber1Section", PolypClassificationOptions.LS
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field_inside_div(
            self.estimate_whole_polyp_size_string, "divPolypNumber1Section", "15"
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            self.polyp_access_string,
            "divPolypNumber1Section",
            PolypAccessOptions.NOT_KNOWN,
        )
        self.polyp1_intervention()
        InvestigationDatasetsPage(self.page).click_add_polyp_button()
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Location", "divPolypNumber2Section", EndoscopyLocationOptions.CAECUM
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Classification", "divPolypNumber2Section", PolypClassificationOptions.LS
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field_inside_div(
            self.estimate_whole_polyp_size_string, "divPolypNumber2Section", "15"
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            self.polyp_access_string,
            "divPolypNumber2Section",
            PolypAccessOptions.NOT_KNOWN,
        )
        InvestigationDatasetsPage(self.page).click_polyp2_add_intervention_button()
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Modality",
            "divPolypTherapy2_1Section",
            PolypInterventionModalityOptions.EMR,
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Device",
            "divPolypTherapy2_1Section",
            PolypInterventionDeviceOptions.HOT_SNARE,
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Excised", "divPolypResected2_1", YesNoOptions.YES
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Retrieved", "divPolypTherapy2_1Section", YesNoOptions.NO
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Excision Technique",
            "divPolypTherapy2_1Section",
            PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        )

    def polyps_for_lnpcp_result(self) -> None:
        # Polyp Information
        InvestigationDatasetsPage(self.page).click_add_polyp_button()
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Location", "divPolypNumber1Section", EndoscopyLocationOptions.ILEUM
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Classification", "divPolypNumber1Section", PolypClassificationOptions.LS
        )
        DatasetFieldUtil(self.page).populate_input_locator_for_field_inside_div(
            self.estimate_whole_polyp_size_string, "divPolypNumber1Section", "30"
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            self.polyp_access_string,
            "divPolypNumber1Section",
            PolypAccessOptions.NOT_KNOWN,
        )
        self.polyp1_intervention()

    def polyp1_intervention(self) -> None:
        InvestigationDatasetsPage(self.page).click_polyp1_add_intervention_button()
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Modality",
            "divPolypTherapy1_1Section",
            PolypInterventionModalityOptions.POLYPECTOMY,
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Device",
            "divPolypTherapy1_1Section",
            PolypInterventionDeviceOptions.HOT_SNARE,
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Excised", "divPolypResected1_1", YesNoOptions.YES
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Retrieved", "divPolypTherapy1_1Section", YesNoOptions.NO
        )
        DatasetFieldUtil(self.page).populate_select_locator_for_field_inside_div(
            "Excision Technique",
            "divPolypTherapy1_1Section",
            PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        )

    def save_investigation_dataset(self) -> None:
        InvestigationDatasetsPage(self.page).check_dataset_complete_checkbox()
        InvestigationDatasetsPage(self.page).click_save_dataset_button()


class AfterInvestigationDatasetComplete:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.a318_latest_event_status_string = (
            "A318 - Post-investigation Appointment NOT Required - Result Letter Created"
        )

    def progress_episode_based_on_result(self, result: str, younger: bool):
        if result == InvestigationDatasetResults.HIGH_RISK:
            self.after_high_risk_result()
            if younger:
                self.record_diagnosis_date()
            else:
                self.handover_subject_to_symptomatic_care()
        elif result == InvestigationDatasetResults.LNPCP:
            self.after_lnpcp_result()
            if younger:
                self.record_diagnosis_date()
            else:
                self.handover_subject_to_symptomatic_care()
        elif result == InvestigationDatasetResults.NORMAL:
            self.after_normal_result()
            self.record_diagnosis_date()
        else:
            logging.error("Incorrect result entered")

    def after_high_risk_result(self) -> None:
        InvestigationDatasetsPage(self.page).expect_text_to_be_visible(
            "High-risk findings"
        )
        BasePage(self.page).click_back_button()

        # The following code is on the subject datasets page
        SubjectDatasetsPage(self.page).check_investigation_dataset_complete()
        BasePage(self.page).click_back_button()

        SubjectScreeningSummaryPage(
            self.page
        ).click_advance_fobt_screening_episode_button()
        # The following code is on the advance fobt screening episode page
        AdvanceFOBTScreeningEpisodePage(
            self.page
        ).click_enter_diagnostic_test_outcome_button()

        # The following code is on the diagnostic test outcome page
        DiagnosticTestOutcomePage(self.page).verify_diagnostic_test_outcome(
            "High-risk findings"
        )
        DiagnosticTestOutcomePage(self.page).select_test_outcome_option(
            OutcomeOfDiagnosticTest.REFER_SURVEILLANCE
        )
        DiagnosticTestOutcomePage(self.page).click_save_button()

    def after_lnpcp_result(self) -> None:
        InvestigationDatasetsPage(self.page).expect_text_to_be_visible("LNPCP")
        BasePage(self.page).click_back_button()

        # The following code is on the subject datasets page
        SubjectDatasetsPage(self.page).check_investigation_dataset_complete()
        BasePage(self.page).click_back_button()

        SubjectScreeningSummaryPage(
            self.page
        ).click_advance_fobt_screening_episode_button()

        # The following code is on the advance fobt screening episode page
        AdvanceFOBTScreeningEpisodePage(
            self.page
        ).click_enter_diagnostic_test_outcome_button()

        # The following code is on the diagnostic test outcome page
        DiagnosticTestOutcomePage(self.page).verify_diagnostic_test_outcome("LNPCP")
        DiagnosticTestOutcomePage(self.page).select_test_outcome_option(
            OutcomeOfDiagnosticTest.REFER_SURVEILLANCE
        )
        DiagnosticTestOutcomePage(self.page).click_save_button()

    def after_normal_result(self):
        InvestigationDatasetsPage(self.page).expect_text_to_be_visible(
            "Normal (No Abnormalities"
        )
        BasePage(self.page).click_back_button()

        # The following code is on the subject datasets page
        SubjectDatasetsPage(self.page).check_investigation_dataset_complete()
        BasePage(self.page).click_back_button()

        SubjectScreeningSummaryPage(
            self.page
        ).click_advance_fobt_screening_episode_button()

        # The following code is on the advance fobt screening episode page
        AdvanceFOBTScreeningEpisodePage(
            self.page
        ).click_enter_diagnostic_test_outcome_button()

        # The following code is on the diagnostic test outcome page
        DiagnosticTestOutcomePage(self.page).verify_diagnostic_test_outcome(
            "Normal (No Abnormalities"
        )
        DiagnosticTestOutcomePage(self.page).select_test_outcome_option(
            OutcomeOfDiagnosticTest.INVESTIGATION_COMPLETE
        )
        DiagnosticTestOutcomePage(self.page).click_save_button()

        SubjectScreeningSummaryPage(self.page).verify_latest_event_status_value(
            self.a318_latest_event_status_string
        )

    def handover_subject_to_symptomatic_care(self) -> None:
        SubjectScreeningSummaryPage(self.page).verify_latest_event_status_value(
            "A394 - Handover into Symptomatic Care for Surveillance - Patient Age"
        )
        SubjectScreeningSummaryPage(
            self.page
        ).click_advance_fobt_screening_episode_button()

        # The following code is on the advance fobt screening episode page
        AdvanceFOBTScreeningEpisodePage(
            self.page
        ).click_handover_into_symptomatic_care_button()

        # The following code is on the handover into symptomatic care page
        HandoverIntoSymptomaticCarePage(self.page).select_referral_dropdown_option(
            "20445"
        )
        HandoverIntoSymptomaticCarePage(self.page).click_calendar_button()
        CalendarPicker(self.page).v1_calender_picker(datetime.today())
        HandoverIntoSymptomaticCarePage(self.page).select_consultant("201")
        HandoverIntoSymptomaticCarePage(self.page).fill_notes("Test Automation")
        HandoverIntoSymptomaticCarePage(self.page).click_save_button()

        SubjectScreeningSummaryPage(self.page).wait_for_page_title()
        SubjectScreeningSummaryPage(self.page).verify_latest_event_status_value(
            "A385 - Handover into Symptomatic Care"
        )

    def record_diagnosis_date(self):
        SubjectScreeningSummaryPage(self.page).verify_latest_event_status_value(
            self.a318_latest_event_status_string
        )
        SubjectScreeningSummaryPage(
            self.page
        ).click_advance_fobt_screening_episode_button()

        # The following code is on the advance fobt screening episode page
        AdvanceFOBTScreeningEpisodePage(self.page).click_record_diagnosis_date_button()

        # The following code is on the record diagnosis date page
        RecordDiagnosisDatePage(self.page).enter_date_in_diagnosis_date_field(
            datetime.today()
        )
        RecordDiagnosisDatePage(self.page).click_save_button()

        SubjectScreeningSummaryPage(self.page).verify_latest_event_status_value(
            self.a318_latest_event_status_string
        )
