# Create a new util that can populate the investigations dataset to get the following
# results:

# High risk
# LNPCP
# Normal

# This needs to be done as there is a lot of repeat code between the three results
# and we need 2 subjects with high risk and LNPCP results.
# Also create any utils to reduce the amount of duplicated code
# to as close to 0% as possible.

# Add utility guide

from pages.datasets.investigation_dataset_page import InvestigationDatasetsPage
from playwright.sync_api import Page


# Populate investigation dataset to get HIGH RISK results
def populate_investigation_dataset_high_risk(page: Page) -> None:
    """
    This populates the investigation dataset to get HIGH RISK results

    Args:
        page (Page): This is the playwright page object
    """
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
    InvestigationDatasetsPage(page).click_add_new_investigation_dataset_button()
    InvestigationDatasetsPage(page).select_investigation_dataset_type("Normal")
    InvestigationDatasetsPage(page).click_save_button()
