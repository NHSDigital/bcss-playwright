import pytest
from playwright.sync_api import Page
from utils.user_tools import UserTools
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
from utils.batch_processing import batch_processing
from pages.logout.log_out_page import LogoutPage
from utils.investigation_dataset import (
    InvestigationDatasetCompletion,
    InvestigationDatasetResults,
    AfterInvestigationDatasetComplete,
)
import logging


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
    # Older patient
    logging.info("High-risk result for an older subject")
    nhs_no = "9104989449"
    InvestigationDatasetCompletion(page).complete_with_result(
        nhs_no, InvestigationDatasetResults.HIGH_RISK
    )
    AfterInvestigationDatasetComplete(page).progress_episode_based_on_result(
        InvestigationDatasetResults.HIGH_RISK, False
    )

    # Younger patient
    logging.info("High-risk result for a younger subject")
    nhs_no = "9160670894"
    InvestigationDatasetCompletion(page).complete_with_result(
        nhs_no, InvestigationDatasetResults.HIGH_RISK
    )
    AfterInvestigationDatasetComplete(page).progress_episode_based_on_result(
        InvestigationDatasetResults.HIGH_RISK, True
    )

    # This needs to be repeated for two subjects, one old and one not - LNPCP Result
    # Older patient
    logging.info("LNPCP result for an older subject")
    nhs_no = "9661266328"
    InvestigationDatasetCompletion(page).complete_with_result(
        nhs_no, InvestigationDatasetResults.LNPCP
    )
    AfterInvestigationDatasetComplete(page).progress_episode_based_on_result(
        InvestigationDatasetResults.LNPCP, False
    )

    # Younger patient
    logging.info("LNPCP result for a younger subject")
    nhs_no = "9345483594"
    InvestigationDatasetCompletion(page).complete_with_result(
        nhs_no, InvestigationDatasetResults.LNPCP
    )
    AfterInvestigationDatasetComplete(page).progress_episode_based_on_result(
        InvestigationDatasetResults.LNPCP, True
    )

    # This needs to be repeated for 1 subject, age does not matter - Normal Result
    logging.info("Normal result for any age subject")
    nhs_no_normal = "9029243430"
    InvestigationDatasetCompletion(page).complete_with_result(
        nhs_no_normal, InvestigationDatasetResults.NORMAL
    )
    AfterInvestigationDatasetComplete(page).progress_episode_based_on_result(
        InvestigationDatasetResults.NORMAL, True
    )

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

    # This is to check for the status of a normal subject as this NHS Number cannot be retrieved from the DB
    verify_subject_event_status_by_nhs_no(
        page, nhs_no_normal, "S61 - Normal (No Abnormalities Found)"
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
