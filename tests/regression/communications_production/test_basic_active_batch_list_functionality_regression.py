import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.communication_production.communications_production_page import (
    CommunicationsProductionPage,
)
from pages.communication_production.batch_list_page import ActiveBatchListPage
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the
    reports page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Go to active batch list page via the communications production page
    BasePage(page).go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_active_batch_list_page()


@pytest.mark.regression
def test_headings_on_active_batch_list_screen(page: Page) -> None:
    """
    Confirms that the active batch list table contains a sortable and filterable column for "ID", "Type", "Original",
    "Event Code", "Description", "Batch Split By", "Screening Centre", "Status", "Priority", "Deadline" and "Count"
    """
    # Active batch list page loads as expected
    ActiveBatchListPage(page).verify_deadline_date_filter_input
