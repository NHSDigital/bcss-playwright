import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.communication_production.communications_production_page import (
    CommunicationsProductionPage,
)
from pages.communication_production.batch_list_page import ActiveBatchListPage
from utils.user_tools import UserTools
from pages.communication_production.manage_active_batch_page import (
    ManageActiveBatchPage,
)


@pytest.fixture
def select_user(page: Page):
    def _login_as(user_role: str):
        # Log in with the specified user
        UserTools.user_login(page, user_role)
        # Navigate to Active Batch List
        BasePage(page).go_to_communications_production_page()
        CommunicationsProductionPage(page).go_to_active_batch_list_page()
        return page

    return _login_as


@pytest.mark.letters_tests
@pytest.mark.regression
def test_headings_on_active_batch_list_screen(select_user) -> None:
    """
    Scenario: Check headings on Active Batch List Screen
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the active batch list
    Then the table contains a sortable and filterable column for "<Column Name>"
    """
    page = select_user("Hub Manager at BCS01")
    batch_list_page = ActiveBatchListPage(page)

    expected_columns = [
        "ID",
        "Type",
        "Original",
        "Event Code",
        "Description",
        "Batch Split By",
        "Screening Centre",
        "Status",
        "Priority",
        "Deadline",
        "Count",
    ]

    for column in expected_columns:
        # Step 1: Ensure the column is present
        batch_list_page.assert_column_present(column)

        # Step 2: Assert sortable UI attribute is present
        batch_list_page.assert_column_sortable(column)

        # Step 3: Assert filterable control is rendered
        batch_list_page.assert_column_filterable(column)


@pytest.mark.letters_tests
@pytest.mark.regression
def test_navigation_to_manage_active_batch_screen(select_user) -> None:
    """
    Scenario: Check navigation from Active Batch List Screen to Manage Active Batch Screen
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the active batch list
    And I select an active batch
    Then I view the details of an active batch
    """
    page = select_user("Hub Manager at BCS01")
    batch_list_page = ActiveBatchListPage(page)

    # Step 1: Ensure the batch list table is visible
    batch_list_page.assert_batch_table_visible()

    # Step 2: Click into the first available batch link (usually ID column)
    batch_list_page.select_first_active_batch()

    # Step 3: Assert navigation to the Manage Active Batch page
    manage_batch_page = ManageActiveBatchPage(page)
    manage_batch_page.assert_batch_details_visible()
