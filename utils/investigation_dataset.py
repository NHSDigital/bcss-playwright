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

from pages.datasets.investigation_dataset_page import InvestigationDatasetsPage
from playwright.sync_api import Page
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage

# This is used to navigate to the investigation datasets page
def go_to_investigation_datasets_page(page: Page, nhs_no) -> None:
    """This is used to navigate to the investigation datasets page
    Args:
        page (Page): This is the playwright page object
        nhs_no (str): The NHS number of the subject
    """
    verify_subject_event_status_by_nhs_no(
        page, nhs_no, "A323 - Post-investigation Appointment NOT Required"
    )

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()


# Populate investigation dataset to get HIGH RISK results
def populate_investigation_dataset_high_risk(page: Page) -> None:
    """
    This populates the investigation dataset to get HIGH RISK results

    Args:
        page (Page): This is the playwright page object
    """
    # default_investigation_dataset_forms(page)
    # InvestigationDatasetsPage(page).select_theraputic_procedure_type()
    # default_investigation_dataset_forms_continuation(page)
    # investigation_datasets_failure_reason(page)
    # polyps_for_high_risk_result(page)
    # save_investigation_dataset(page)
    # after_high_risk_result(page)
    InvestigationDatasetsPage(page).click_add_new_investigation_dataset_button()
    InvestigationDatasetsPage(page).select_investigation_dataset_type("High Risk")
    InvestigationDatasetsPage(page).click_save_button()


# Populate investigation dataset to get LNPCP results
def populate_investigation_dataset_lnpcp(page: Page) -> None:
    """
    This populates the investigation dataset to get LNPCP results

    Args:
        page (Page): This is the playwright page object
    """
    # default_investigation_dataset_forms(page)
    # InvestigationDatasetsPage(page).select_theraputic_procedure_type()
    # default_investigation_dataset_forms_continuation(page)
    # investigation_datasets_failure_reason(page)
    # polyps_for_lnpcp_result(page)
    # save_investigation_dataset(page)
    # after_lnpcp_result(page)
    InvestigationDatasetsPage(page).click_add_new_investigation_dataset_button()
    InvestigationDatasetsPage(page).select_investigation_dataset_type("LNPCP")
    InvestigationDatasetsPage(page).click_save_button()


# Populate investigation dataset to get NORMAL results
def populate_investigation_dataset_normal(page: Page) -> None:
    """
    This populates the investigation dataset to get NORMAL results

    Args:
        page (Page): This is the playwright page object
    """
    # default_investigation_dataset_forms(page)
    # InvestigationDatasetsPage(page).select_diagnostic_procedure_type()
    # default_investigation_dataset_forms_continuation(page)
    # InvestigationDatasetsPage(page).click_show_failure_information()
    # InvestigationDatasetsPage(page).select_failure_reasons_option(
    #     FailureReasonsOptions.NO_FAILURE_REASONS
    # )
    # save_investigation_dataset(page)
    # InvestigationDatasetsPage(page).expect_text_to_be_visible(
    #     "Normal (No Abnormalities"
    # )
    InvestigationDatasetsPage(page).click_add_new_investigation_dataset_button()
    InvestigationDatasetsPage(page).select_investigation_dataset_type("Normal")
    InvestigationDatasetsPage(page).click_save_button()
