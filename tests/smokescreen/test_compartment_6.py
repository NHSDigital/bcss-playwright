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


@pytest.mark.vpn_required
@pytest.mark.smokescreen
@pytest.mark.compartment5
def test_compartment_5(page: Page, smokescreen_properties: dict) -> None:
    """
    This is the main compartment 6 method
    Filling out the investigation datasets for different subjects to get different results for a diagnostic test.
    Printing the diagnostic test result letters.
    """

    # For the following tests old referes to if they are over 75 at recall
    # The recall period is 2 years from the last diagnostic test for a Normal or Abnormal diagnostic test result
    # or 3 years for someone who is going in to Surveillance (High-risk findings or LNPCP)

    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # This needs to be repeated for two subjects, one old and one not - High Risk Result
    nhs_no = "9619187075"
    verify_subject_event_status_by_nhs_no(
        page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
    )

    SubjectScreeningSummaryPage(page).click_datasets_link()

    page.locator("div").filter(
        has_text="Investigation (1 Dataset) Show Dataset"
    ).get_by_role("link").click()
    page.locator("#UI_SITE_SELECT_LINK").click()
    page.locator("#UI_RESULTS_rljsjnkh").select_option("35317")
    page.locator("#UI_SSP_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_okdvpfko").select_option("1251")
    page.locator("#UI_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_sawaeghr").select_option("886")
    page.locator("#UI_ASPIRANT_ENDOSCOPIST_PIO_SELECT_LINK").click()
    page.locator("#anchorDrug").click()
    page.locator("#UI_BOWEL_PREP_DRUG1").select_option("200537~Tablet(s)")
    page.locator("#UI_BOWEL_PREP_DRUG_DOSE1").click()
    page.locator("#UI_BOWEL_PREP_DRUG_DOSE1").fill("10")
    page.get_by_role("link", name="Show details").click()
    page.locator("#radScopeInsertedYes").check()
    page.get_by_role("radio", name="Therapeutic").check()
    page.get_by_label("Bowel preparation quality").select_option("17016")
    page.get_by_label("Comfort during examination").select_option("18505")
    page.get_by_label("Comfort during recovery").select_option("18505")
    page.get_by_label("Endoscopist defined extent").select_option(
        "17240~Colonoscopy Complete"
    )
    page.get_by_label("Scope imager used").select_option("17058")
    page.get_by_label("Retroverted view").select_option("17059")
    page.get_by_role("textbox", name="Start of intubation time").click()
    page.get_by_role("textbox", name="Start of intubation time").fill("09:00")
    page.get_by_role("textbox", name="Start of extubation time").click()
    page.get_by_role("textbox", name="Start of extubation time").fill("09:15")
    page.get_by_role("textbox", name="End time of procedure").click()
    page.get_by_role("textbox", name="End time of procedure").fill("09:30")
    page.get_by_role("textbox", name="Scope ID").click()
    page.get_by_role("textbox", name="Scope ID").fill("A1")
    page.get_by_label("Insufflation").select_option("200547")
    page.get_by_label("Outcome at time of procedure").select_option(
        "17148~Complications are optional"
    )
    page.get_by_label("Late outcome").select_option(
        "17216~Complications are not required"
    )
    page.locator("#anchorCompletionProof").click()
    page.get_by_label("Proof Parameters").select_option("200575")
    page.locator("#anchorFailure").click()
    page.get_by_label("Failure Reasons").select_option("205148")
    page.get_by_role("button", name="Add Polyp").click()
    page.locator("#UI_POLYP_LOCATION1").select_option("17240~Colonoscopy Complete")
    page.get_by_label("Classification ?").select_option("17295")
    page.get_by_role("textbox", name="Estimate of whole polyp size").click()
    page.get_by_role("textbox", name="Estimate of whole polyp size").fill("15")
    page.get_by_label("Polyp Access").select_option("17060")
    page.get_by_role("link", name="Add Intervention").click()
    page.locator("#UI_POLYP_THERAPY_MODALITY1_1").select_option("17189~Resection")
    page.locator("#UI_DEVICE1_1").select_option("17070")
    page.get_by_label("Excised").select_option("17058")
    page.get_by_label("Retrieved").select_option("17059")
    page.get_by_label("Excision Technique").select_option("17751")
    page.get_by_role("button", name="Add Polyp").click()
    page.locator("#UI_POLYP_LOCATION2").select_option("17239~Colonoscopy Complete")
    page.locator("#UI_POLYP_CLASS2").select_option("17295")
    page.locator("#UI_POLYP_SIZE2").click()
    page.locator("#UI_POLYP_SIZE2").fill("15")
    page.locator("#UI_POLYP_ACCESS2").select_option("17060")
    page.locator("#spanPolypInterventionLink2").get_by_role(
        "link", name="Add Intervention"
    ).click()
    page.locator("#UI_POLYP_THERAPY_MODALITY2_1").select_option("17193~Resection")
    page.locator("#UI_DEVICE2_1").select_option("17070")
    page.locator("#UI_POLYP_RESECTED2_1").select_option("17058")
    page.locator("#UI_POLYP_RETRIEVED2_1").select_option("17059")
    page.locator("#UI_POLYP_REMOVAL_TYPE2_1").select_option("17751")
    page.locator("#radDatasetCompleteYes").check()
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#UI_DIV_BUTTON_SAVE1").get_by_role(
        "button", name="Save Dataset"
    ).click()

    expect(page.get_by_text("High-risk findings")).to_be_visible()
    page.get_by_role("link", name="Back").click()
    expect(page.get_by_text("** Completed **").nth(1)).to_be_visible()
    page.get_by_role("link", name="Back").click()

    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Enter Diagnostic Test Outcome").click()
    expect(page.get_by_role("cell", name="High-risk findings").nth(1)).to_be_visible()
    page.get_by_label("Outcome of Diagnostic Test").select_option("20365")
    page.get_by_role("button", name="Save").click()

    # This is if the subject is too old
    expect(
        page.get_by_role(
            "cell",
            name="A394 - Handover into Symptomatic Care for Surveillance - Patient Age",
            exact=True,
        )
    ).to_be_visible()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Handover into Symptomatic Care").click()
    page.get_by_label("Referral").select_option("20445")
    page.get_by_role("button", name="Calendar").click()
    page.get_by_role("cell", name="9", exact=True).click()
    page.locator("#UI_NS_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_usgwmbob").select_option("201")
    page.locator("#UI_NS_PRACTITIONER_PIO_SELECT_LINK").click()
    page.get_by_role("textbox", name="Notes").click()
    page.get_by_role("textbox", name="Notes").fill("Test Automation")
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Save").click()
    expect(
        page.get_by_role(
            "cell", name="A385 - Handover into Symptomatic Care", exact=True
        )
    ).to_be_visible()

    # This is if the subject is not too old
    expect(
        page.get_by_role(
            "cell",
            name="A318 - Post-investigation Appointment NOT Required - Result Letter Created",
            exact=True,
        )
    ).to_be_visible()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    page.locator("#diagnosisDate").click()
    page.locator("#diagnosisDate").fill("09 May 2025")
    page.get_by_role("button", name="Save").click()
    expect(
        page.get_by_role(
            "cell",
            name="A318 - Post-investigation Appointment NOT Required - Result Letter Created",
            exact=True,
        )
    ).to_be_visible()  #

    # This needs to be repeated for two subjects, one old and one not - LBPCP Result
    nhs_no = "9619187075"
    verify_subject_event_status_by_nhs_no(
        page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
    )

    SubjectScreeningSummaryPage(page).click_datasets_link()

    page.locator("div").filter(
        has_text="Investigation (1 Dataset) Show Dataset"
    ).get_by_role("link").click()
    page.locator("#UI_SITE_SELECT_LINK").click()
    page.locator("#UI_RESULTS_cwfoncwk").select_option("35317")
    page.locator("#UI_SSP_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_hpbvheab").select_option("1251")
    page.locator("#UI_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_ohrfhcdm").select_option("886")
    page.locator("#UI_ASPIRANT_ENDOSCOPIST_PIO_SELECT_LINK").click()
    page.locator("#anchorDrug").click()
    page.locator("#UI_BOWEL_PREP_DRUG1").select_option("200537~Tablet(s)")
    page.locator("#UI_BOWEL_PREP_DRUG_DOSE1").click()
    page.locator("#UI_BOWEL_PREP_DRUG_DOSE1").fill("10")
    page.get_by_role("link", name="Show details").click()
    page.locator("#radScopeInsertedYes").check()
    page.get_by_role("radio", name="Therapeutic").check()
    page.get_by_label("Bowel preparation quality").select_option("17016")
    page.get_by_label("Comfort during examination").select_option("18505")
    page.get_by_label("Comfort during recovery").select_option("18505")
    page.get_by_label("Endoscopist defined extent").select_option(
        "17240~Colonoscopy Complete"
    )
    page.get_by_label("Scope imager used").select_option("17058")
    page.get_by_label("Retroverted view").select_option("17059")
    page.get_by_role("textbox", name="Start of intubation time").click()
    page.get_by_role("textbox", name="Start of intubation time").fill("09:00")
    page.get_by_role("textbox", name="Start of extubation time").click()
    page.get_by_role("textbox", name="Start of extubation time").fill("09:15")
    page.get_by_role("textbox", name="End time of procedure").click()
    page.get_by_role("textbox", name="End time of procedure").fill("09:30")
    page.get_by_role("textbox", name="Scope ID").click()
    page.get_by_role("textbox", name="Scope ID").fill("A1")
    page.get_by_label("Insufflation").select_option("200547")
    page.get_by_label("Outcome at time of procedure").select_option(
        "17148~Complications are optional"
    )
    page.get_by_label("Late outcome").select_option(
        "17216~Complications are not required"
    )
    page.locator("#anchorCompletionProof").click()
    page.get_by_label("Proof Parameters").select_option("200575")
    page.locator("#anchorFailure").click()
    page.get_by_label("Failure Reasons").select_option("205148")
    page.get_by_role("button", name="Add Polyp").click()
    page.locator("#UI_POLYP_LOCATION1").select_option("17240~Colonoscopy Complete")
    page.get_by_label("Classification ?").select_option("17295")
    page.get_by_role("textbox", name="Estimate of whole polyp size").click()
    page.get_by_role("textbox", name="Estimate of whole polyp size").fill("30")
    page.get_by_label("Polyp Access").select_option("17060")
    page.get_by_role("link", name="Add Intervention").click()
    page.locator("#UI_POLYP_THERAPY_MODALITY1_1").select_option("17189~Resection")
    page.locator("#UI_DEVICE1_1").select_option("17070")
    page.get_by_label("Excised").select_option("17058")
    page.get_by_label("Retrieved").select_option("17059")
    page.get_by_label("Excision Technique").select_option("17751")
    page.locator("#radDatasetCompleteYes").check()
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#UI_DIV_BUTTON_SAVE1").get_by_role(
        "button", name="Save Dataset"
    ).click()

    expect(page.get_by_text("LNPCP")).to_be_visible()
    page.get_by_role("link", name="Back").click()
    expect(page.get_by_text("** Completed **").nth(1)).to_be_visible()
    page.get_by_role("link", name="Back").click()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Enter Diagnostic Test Outcome").click()
    expect(page.get_by_role("cell", name="LNPCP").nth(1)).to_be_visible()
    page.get_by_label("Outcome of Diagnostic Test").select_option("20365")
    page.get_by_role("button", name="Save").click()

    # If the subject is too old
    expect(
        page.get_by_role(
            "cell",
            name="A394 - Handover into Symptomatic Care for Surveillance - Patient Age",
            exact=True,
        )
    ).to_be_visible()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Handover into Symptomatic Care").click()
    page.get_by_label("Referral").select_option("20445")
    page.get_by_role("button", name="Calendar").click()
    page.get_by_role("cell", name="9", exact=True).click()
    page.locator("#UI_NS_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_ktdtoepq").select_option("201")
    page.locator("#UI_NS_PRACTITIONER_PIO_SELECT_LINK").click()
    page.get_by_role("textbox", name="Notes").click()
    page.get_by_role("textbox", name="Notes").fill("Test Automation")
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Save").click()
    expect(
        page.get_by_role(
            "cell", name="A385 - Handover into Symptomatic Care", exact=True
        )
    ).to_be_visible()

    # If the subject is not too old
    expect(
        page.get_by_role(
            "cell",
            name="A318 - Post-investigation Appointment NOT Required - Result Letter Created",
            exact=True,
        )
    ).to_be_visible()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    page.locator("#diagnosisDate").click()
    page.locator("#diagnosisDate").fill("09 May 2025")
    page.get_by_role("button", name="Save").click()
    expect(
        page.get_by_role(
            "cell",
            name="A318 - Post-investigation Appointment NOT Required - Result Letter Created",
            exact=True,
        )
    ).to_be_visible()

    # This needs to be repeated for 1 subject, age does not matter - Normal Result
    nhs_no = "9619187075"
    verify_subject_event_status_by_nhs_no(
        page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
    )

    SubjectScreeningSummaryPage(page).click_datasets_link()

    page.locator("#UI_SITE_SELECT_LINK").click()
    page.locator("#UI_RESULTS_mjbnjlos").select_option("35317")
    page.locator("#UI_SSP_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_rquytpri").select_option("1251")
    page.locator("#UI_SSP_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_rquytpri").select_option("1251")
    page.locator("#UI_CONSULTANT_PIO_SELECT_LINK").click()
    page.locator("#UI_RESULTS_mkbtktgp").select_option("886")
    page.locator("#UI_ASPIRANT_ENDOSCOPIST_PIO_SELECT_LINK").click()
    page.locator("#anchorDrug").click()
    page.locator("#UI_BOWEL_PREP_DRUG1").select_option("200537~Tablet(s)")
    page.locator("#UI_BOWEL_PREP_DRUG_DOSE1").click()
    page.locator("#UI_BOWEL_PREP_DRUG_DOSE1").fill("10")
    page.get_by_role("link", name="Show details").click()
    page.locator("#radScopeInsertedYes").check()
    page.get_by_role("radio", name="Diagnostic").check()
    page.get_by_label("Bowel preparation quality").select_option("17016")
    page.get_by_label("Comfort during examination").select_option("18505")
    page.get_by_label("Comfort during recovery").select_option("18505")
    page.get_by_label("Endoscopist defined extent").select_option(
        "17240~Colonoscopy Complete"
    )
    page.get_by_label("Scope imager used").select_option("17058")
    page.get_by_label("Retroverted view").select_option("17059")
    page.get_by_role("textbox", name="Start of intubation time").click()
    page.get_by_role("textbox", name="Start of intubation time").fill("09:00")
    page.get_by_role("textbox", name="Start of extubation time").click()
    page.get_by_role("textbox", name="Start of extubation time").fill("09:15")
    page.get_by_role("textbox", name="End time of procedure").click()
    page.get_by_role("textbox", name="End time of procedure").fill("09:30")
    page.get_by_role("textbox", name="Scope ID").click()
    page.get_by_role("textbox", name="Scope ID").fill("A1")
    page.get_by_label("Insufflation").select_option("200547")
    page.get_by_label("Outcome at time of procedure").select_option(
        "17148~Complications are optional"
    )
    page.get_by_label("Late outcome").select_option(
        "17216~Complications are not required"
    )
    page.locator("#anchorCompletionProof").click()
    page.get_by_label("Proof Parameters").select_option("200575")
    page.locator("#anchorFailure").click()
    page.get_by_label("Failure Reasons").select_option("18500")
    page.locator("#radDatasetCompleteYes").check()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.locator("#UI_DIV_BUTTON_SAVE1").get_by_role(
        "button", name="Save Dataset"
    ).click()
    expect(page.get_by_text("Normal (No Abnormalities")).to_be_visible()
    page.get_by_role("link", name="Back").click()
    expect(page.get_by_text("** Completed **").nth(1)).to_be_visible()
    page.get_by_role("link", name="Back").click()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Enter Diagnostic Test Outcome").click()
    expect(
        page.get_by_role("cell", name="Normal (No Abnormalities").nth(1)
    ).to_be_visible()
    page.get_by_label("Outcome of Diagnostic Test").select_option("")
    page.get_by_label("Outcome of Diagnostic Test").select_option("20360")
    page.get_by_role("button", name="Save").click()
    expect(
        page.get_by_role(
            "cell",
            name="A318 - Post-investigation Appointment NOT Required - Result Letter Created",
            exact=True,
        )
    ).to_be_visible()
    page.get_by_role("button", name="Advance FOBT Screening Episode").click()
    page.get_by_role("button", name="Record Diagnosis Date").click()
    page.locator("#diagnosisDate").click()
    page.locator("#diagnosisDate").fill("09 May 2025")
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
        "A318",
        "Result Letters - No Post-investigation Appointment",
        [
            "S61 - Normal (No Abnormalities Found)",
            "A158 - High-risk findings",
            "A157 - LNPCP",
        ],
    )

    batch_processing(
        "A385",
        "Handover into Symptomatic Care Adenoma Surveillance, Age - GP Letter",
        "A382 - Handover into Symptomatic Care - GP Letter Printed",
    )

    batch_processing(
        "A382",
        "Handover into Symptomatic Care Adenoma Surveillance - Patient Letter",
        "P202 - Waiting Completion of Outstanding Events",
    )

    LogoutPage(page).log_out()
