import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.communication_production.communications_production_page import (
    CommunicationsProductionPage,
)
from pages.communication_production.batch_list_page import (
    ArchivedBatchListPage,
)
from utils.user_tools import UserTools
from pages.communication_production.manage_archived_batch_page import (
    ManageArchivedBatchPage,
)


@pytest.fixture
def select_user(page: Page):
    def _login_as(user_role: str):
        # Log in with the specified user
        UserTools.user_login(page, user_role)
        # Navigate to Active Batch List
        BasePage(page).go_to_communications_production_page()
        CommunicationsProductionPage(page).go_to_archived_batch_list_page()
        return page

    return _login_as


@pytest.mark.letters_tests
@pytest.mark.regression
def test_headings_on_archived_batch_list_screen(select_user) -> None:
    """
    Scenario: Check headings on Archived Batch List Screen
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the archived batch list
    Then the table contains a sortable and filterable column for each expected header
    """
    page = select_user("Hub Manager at BCS01")

    archived_batch_list_page = ArchivedBatchListPage(page)

    expected_columns = [
        "ID",
        "Type",
        "Original",
        "Letter Group",
        "Event Code",
        "Description",
        "Batch Split By",
        "Screening Centre",
        "Status",
        "Priority",
        "Date On Letter",
        "Date Archived",
        "Count",
    ]

    for column in expected_columns:
        # Step 1: Ensure the column is present
        archived_batch_list_page.assert_column_present(column)

        # Step 2: Assert sortable UI attribute is present
        archived_batch_list_page.assert_column_sortable(column)

        # Step 3: Assert filterable control is rendered
        archived_batch_list_page.assert_column_filterable(column)


@pytest.mark.letters_tests
@pytest.mark.regression
def test_navigation_to_manage_archived_batch_screen(select_user) -> None:
    """
    Scenario: Check navigation from Archived Batch List Screen to Manage Archived Batch Screen
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the archived batch list
    And I select an archived batch
    Then I view the details of an archived batch
    """
    page = select_user("Hub Manager at BCS01")
    archived_batch_list_page = ArchivedBatchListPage(page)

    # Step 1: Ensure the archived batch table is visible
    archived_batch_list_page.assert_batch_table_visible()

    # Step 2: Click into the first available archived batch
    archived_batch_list_page.select_first_archived_batch()

    # Step 3: Assert navigation to the Manage Archived Batch page
    manage_batch_page = ManageArchivedBatchPage(page)
    manage_batch_page.assert_batch_details_visible()
