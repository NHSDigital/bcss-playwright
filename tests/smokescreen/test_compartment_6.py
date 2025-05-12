import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.user_tools import UserTools
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils.batch_processing import batch_processing
from pages.logout.log_out_page import LogoutPage
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
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


# This should go into a util. Adding it here to avoid SonarQube duplication errors:
def go_to_investigation_datasets_page(page: Page, nhs_no) -> None:
    verify_subject_event_status_by_nhs_no(
        page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
    )

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()


def deafult_investigation_dataset_forms(page: Page) -> None:
    # Investigation Dataset
    InvestigationDatasetsPage(page).select_site_lookup_option(
        SiteLookupOptions.RL401.value
    )
    InvestigationDatasetsPage(page).select_practitioner_option(
        PractitionerOptions.AMID_SNORING.value
    )
    InvestigationDatasetsPage(page).select_testing_clinician_option(
        TestingClinicianOptions.BORROWING_PROPERTY.value
    )
    InvestigationDatasetsPage(page).select_aspirant_endoscopist_option(
        AspirantEndoscopistOptions.ITALICISE_AMNESTY.value
    )
    # Drug Information
    InvestigationDatasetsPage(page).click_show_drug_information()
    InvestigationDatasetsPage(page).select_drug_type_option1(
        DrugTypeOptions.BISACODYL.value
    )
    InvestigationDatasetsPage(page).fill_drug_type_dose1("10")
    # Ensocopy Information
    InvestigationDatasetsPage(page).click_show_endoscopy_information()
    InvestigationDatasetsPage(page).check_endoscope_inserted_yes()
    InvestigationDatasetsPage(page).select_theraputic_procedure_type()
    InvestigationDatasetsPage(page).select_bowel_preparation_quality_option(
        BowelPreparationQualityOptions.GOOD.value
    )
    InvestigationDatasetsPage(page).select_comfort_during_examination_option(
        ComfortOptions.NO_DISCOMFORT.value
    )
    InvestigationDatasetsPage(page).select_comfort_during_recovery_option(
        ComfortOptions.NO_DISCOMFORT.value
    )
    InvestigationDatasetsPage(page).select_endoscopist_defined_extent_option(
        EndoscopyLocationOptions.ILEUM.value
    )
    InvestigationDatasetsPage(page).select_scope_imager_used_option(
        YesNoOptions.YES.value
    )
    InvestigationDatasetsPage(page).select_retorted_view_option(YesNoOptions.NO.value)
    InvestigationDatasetsPage(page).fill_start_of_intubation_time("09:00")
    InvestigationDatasetsPage(page).fill_start_of_extubation_time("09:15")
    InvestigationDatasetsPage(page).fill_end_time_of_procedure("09:30")
    InvestigationDatasetsPage(page).fill_scope_id("A1")
    InvestigationDatasetsPage(page).select_insufflation_option(
        InsufflationOptions.AIR.value
    )
    InvestigationDatasetsPage(page).select_outcome_at_time_of_procedure_option(
        OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT.value
    )
    InvestigationDatasetsPage(page).select_late_outcome_option(
        LateOutcomeOptions.NO_COMPLICATIONS.value
    )
    InvestigationDatasetsPage(page).click_show_completion_proof_information()
    # Completion Proof Information
    InvestigationDatasetsPage(page).select_completion_proof_option(
        CompletionProofOptions.PHOTO_ILEO.value
    )


def investigation_datasets_failure_reason(page: Page) -> None:
    # Failure Information
    InvestigationDatasetsPage(page).click_show_failure_information()
    InvestigationDatasetsPage(page).select_failure_reasons_option(
        FailureReasonsOptions.BLEEDING_INCIDENT.value
    )


def polyps_for_high_risk_result(page: Page) -> None:
    # Polyp Information
    InvestigationDatasetsPage(page).click_add_polyp_button()
    InvestigationDatasetsPage(page).select_polyp1_location_option(
        EndoscopyLocationOptions.ILEUM.value
    )
    InvestigationDatasetsPage(page).select_polyp1_classification_option(
        PolypClassificationOptions.LS.value
    )
    InvestigationDatasetsPage(page).fill_polyp1_size("15")
    InvestigationDatasetsPage(page).select_polyp1_access_option(
        PolypAccessOptions.NOT_KNOWN.value
    )
    polyp1_intervention(page)
    InvestigationDatasetsPage(page).click_add_polyp_button()
    InvestigationDatasetsPage(page).select_polyp2_location_option(
        EndoscopyLocationOptions.CAECUM.value
    )
    InvestigationDatasetsPage(page).select_polyp2_classification_option(
        PolypClassificationOptions.LS.value
    )
    InvestigationDatasetsPage(page).fill_polyp2_size("15")
    InvestigationDatasetsPage(page).select_polyp2_access_option(
        PolypAccessOptions.NOT_KNOWN.value
    )
    InvestigationDatasetsPage(page).click_polyp2_add_intervention_button()
    InvestigationDatasetsPage(page).select_polyp2_intervention_modality_option(
        PolypInterventionModalityOptions.EMR.value
    )
    InvestigationDatasetsPage(page).select_polyp2_intervention_device_option(
        PolypInterventionDeviceOptions.HOT_SNARE.value
    )
    InvestigationDatasetsPage(page).select_polyp2_intervention_excised_option(
        YesNoOptions.YES.value
    )
    InvestigationDatasetsPage(page).select_polyp2_intervention_retrieved_option(
        YesNoOptions.NO.value
    )
    InvestigationDatasetsPage(
        page
    ).select_polyp2_intervention_excision_technique_option(
        PolypInterventionExcisionTechniqueOptions.EN_BLOC.value
    )


def polyps_for_lnpcp_result(page: Page) -> None:
    # Polyp Information
    InvestigationDatasetsPage(page).click_add_polyp_button()
    InvestigationDatasetsPage(page).select_polyp1_location_option(
        EndoscopyLocationOptions.ILEUM.value
    )
    InvestigationDatasetsPage(page).select_polyp1_classification_option(
        PolypClassificationOptions.LS.value
    )
    InvestigationDatasetsPage(page).fill_polyp1_size("30")
    InvestigationDatasetsPage(page).select_polyp1_access_option(
        PolypAccessOptions.NOT_KNOWN.value
    )
    polyp1_intervention(page)


def polyp1_intervention(page: Page) -> None:
    InvestigationDatasetsPage(page).click_polyp1_add_intervention_button()
    InvestigationDatasetsPage(page).select_polyp1_intervention_modality_option(
        PolypInterventionModalityOptions.POLYPECTOMY.value
    )
    InvestigationDatasetsPage(page).select_polyp1_intervention_device_option(
        PolypInterventionDeviceOptions.HOT_SNARE.value
    )
    InvestigationDatasetsPage(page).select_polyp1_intervention_excised_option(
        YesNoOptions.YES.value
    )
    InvestigationDatasetsPage(page).select_polyp1_intervention_retrieved_option(
        YesNoOptions.NO.value
    )
    InvestigationDatasetsPage(
        page
    ).select_polyp1_intervention_excision_technique_option(
        PolypInterventionExcisionTechniqueOptions.EN_BLOC.value
    )


def save_investigation_dataset(page: Page) -> None:
    InvestigationDatasetsPage(page).check_dataset_complete_checkbox()
    InvestigationDatasetsPage(page).click_save_dataset_button()


@pytest.mark.vpn_required
@pytest.mark.smokescreen
@pytest.mark.compartment6
def test_compartment_6(page: Page, smokescreen_properties: dict) -> None:
    """
    This is the main compartment 6 method
    Filling out the investigation datasets for different subjects to get different results for a diagnostic test.
    Printing the diagnostic test result letters.
    """

    # For the following tests old refers to if they are over 75 at recall
    # The recall period is 2 years from the last diagnostic test for a Normal or Abnormal diagnostic test result
    # or 3 years for someone who is going in to Surveillance (High-risk findings or LNPCP)

    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # This needs to be repeated for two subjects, one old and one not - High Risk Result
    nhs_no = "9160670894"  # Dummy NHS Number (will not work)
    go_to_investigation_datasets_page(page, nhs_no)

    # The following code is on the investigation datasets page
    deafult_investigation_dataset_forms(page)
    investigation_datasets_failure_reason(page)
    polyps_for_high_risk_result(page)
    save_investigation_dataset(page)

    InvestigationDatasetsPage(page).expect_text_to_be_visible("High-risk findings")
    BasePage(page).click_back_button()

    # The following code is on the subject datasets page
    expect(page.get_by_text("** Completed **").nth(1)).to_be_visible()
    BasePage(page).click_back_button()

    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()
    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Enter Diagnostic Test Outcome").click()
    # The following code is on the diagnostic test outcome page
    expect(page.get_by_role("cell", name="High-risk findings").nth(1)).to_be_visible()
    page.get_by_label("Outcome of Diagnostic Test").select_option("20365")
    page.get_by_role("button", name="Save").click()

    # This is if the subject is too old
    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A394 - Handover into Symptomatic Care for Surveillance - Patient Age"
    )
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Handover into Symptomatic Care").click()

    # The following code is on the handover into symptomatic care page
    page.get_by_label("Referral").select_option("20445")
    page.get_by_role("button", name="Calendar").click()
    page.get_by_role(
        "cell", name="9", exact=True
    ).click()  # Todays date (v1 calendar picker)
    page.locator("#UI_NS_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_usgwmbob").select_option("201")
    page.locator("#UI_NS_PRACTITIONER_PIO_SELECT_LINK").click()
    page.get_by_role("textbox", name="Notes").click()
    page.get_by_role("textbox", name="Notes").fill("Test Automation")
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Save").click()

    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A385 - Handover into Symptomatic Care"
    )

    # This is if the subject is not too old
    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A318 - Post-investigation Appointment NOT Required - Result Letter Created"
    )
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Record Diagnosis Date").click()

    # The following code is on the record diagnosis date page
    page.locator("#diagnosisDate").click()
    page.locator("#diagnosisDate").fill("09 May 2025")  # Todays date
    page.get_by_role("button", name="Save").click()

    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A318 - Post-investigation Appointment NOT Required - Result Letter Created"
    )

    # This needs to be repeated for two subjects, one old and one not - LNPCP Result
    nhs_no = "9619187076"  # Dummy NHS Number (will not work)
    go_to_investigation_datasets_page(page, nhs_no)

    # The following code is on the investigation datasets page
    deafult_investigation_dataset_forms(page)
    investigation_datasets_failure_reason(page)
    polyps_for_lnpcp_result(page)
    save_investigation_dataset(page)

    InvestigationDatasetsPage(page).expect_text_to_be_visible("LNPCP")
    BasePage(page).click_back_button()

    # The following code is on the subject datasets page
    expect(page.get_by_text("** Completed **").nth(1)).to_be_visible()
    BasePage(page).click_back_button()

    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Enter Diagnostic Test Outcome").click()

    # The following code is on the diagnostic test outcome page
    expect(page.get_by_role("cell", name="LNPCP").nth(1)).to_be_visible()
    page.get_by_label("Outcome of Diagnostic Test").select_option("20365")
    page.get_by_role("button", name="Save").click()

    # If the subject is too old
    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A394 - Handover into Symptomatic Care for Surveillance - Patient Age"
    )
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Handover into Symptomatic Care").click()

    # The following code is on the handover into symptomatic care page
    page.get_by_label("Referral").select_option("20445")
    page.get_by_role("button", name="Calendar").click()
    page.get_by_role(
        "cell", name="9", exact=True
    ).click()  # Todays date (v1 calendar picker)
    page.locator("#UI_NS_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_ktdtoepq").select_option("201")
    page.locator("#UI_NS_PRACTITIONER_PIO_SELECT_LINK").click()
    page.get_by_role("textbox", name="Notes").click()
    page.get_by_role("textbox", name="Notes").fill("Test Automation")
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Save").click()

    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A385 - Handover into Symptomatic Care"
    )

    # If the subject is not too old
    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A318 - Post-investigation Appointment NOT Required - Result Letter Created"
    )
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Record Diagnosis Date").click()

    # The following code is on the record diagnosis date page
    page.locator("#diagnosisDate").click()
    page.locator("#diagnosisDate").fill("09 May 2025")  # Todays date
    page.get_by_role("button", name="Save").click()

    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A318 - Post-investigation Appointment NOT Required - Result Letter Created"
    )

    # This needs to be repeated for 1 subject, age does not matter - Normal Result
    nhs_no = "9619187077"  # Dummy NHS Number (will not work)
    go_to_investigation_datasets_page(page, nhs_no)

    # The following code is on the investigation datasets page
    deafult_investigation_dataset_forms(page)
    InvestigationDatasetsPage(page).click_show_failure_information()
    InvestigationDatasetsPage(page).select_failure_reasons_option(
        FailureReasonsOptions.NO_FAILURE_REASONS.value
    )
    save_investigation_dataset(page)
    InvestigationDatasetsPage(page).expect_text_to_be_visible(
        "Normal (No Abnormalities"
    )
    BasePage(page).click_back_button()

    # The following code is on the subject datasets page
    expect(page.get_by_text("** Completed **").nth(1)).to_be_visible()
    BasePage(page).click_back_button()

    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Enter Diagnostic Test Outcome").click()

    # The following code is on the diagnostic test outcome page
    expect(
        page.get_by_role("cell", name="Normal (No Abnormalities").nth(1)
    ).to_be_visible()
    page.get_by_label("Outcome of Diagnostic Test").select_option("")
    page.get_by_label("Outcome of Diagnostic Test").select_option("20360")
    page.get_by_role("button", name="Save").click()

    SubjectScreeningSummaryPage(page).verify_latest_event_status_value(
        "A318 - Post-investigation Appointment NOT Required - Result Letter Created"
    )
    SubjectScreeningSummaryPage(page).click_advance_fobt_screening_episode_button()

    # The following code is on the advance fobt screening episode page
    page.get_by_role("button", name="Record Diagnosis Date").click()

    # The following code is on the record diagnosis date page
    page.locator("#diagnosisDate").click()
    page.locator("#diagnosisDate").fill("09 May 2025")  # Todays date
    page.get_by_role("button", name="Save").click()

    # Modification needs to be done to accept this list. it should check if any of the values in this list are present. Something like the following:
    # def get_first_visible_cell(page, values):
    # if isinstance(values, str):
    #     values = [values]
    # for name in values:
    #     locator = page.get_by_role("cell", name=name)
    #     if locator.is_visible():
    #         return locator

    batch_processing(
        page,
        "A318",
        "Result Letters - No Post-investigation Appointment",
        [
            "S61 - Normal (No Abnormalities Found)",
            "A158 - High-risk findings",
            "A157 - LNPCP",
        ],
    )

    batch_processing(
        page,
        "A385",
        "Handover into Symptomatic Care Adenoma Surveillance, Age - GP Letter",
        "A382 - Handover into Symptomatic Care - GP Letter Printed",
    )

    batch_processing(
        page,
        "A382",
        "Handover into Symptomatic Care Adenoma Surveillance - Patient Letter",
        "P202 - Waiting Completion of Outstanding Events",
    )

    LogoutPage(page).log_out()
