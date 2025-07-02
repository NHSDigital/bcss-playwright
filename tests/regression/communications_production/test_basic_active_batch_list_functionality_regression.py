import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.communication_production.communications_production_page import (
    CommunicationsProductionPage,
)
from pages.communication_production.batch_list_page import ActiveBatchListPage
from utils.user_tools import UserTools
from utils.table_util import TableUtils


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

# @BCSSAdditionalTests @LettersTests
# Feature: Basic Active Batch List functionality

# Scenario: Check navigation from Active Batch List Screen to Manage Active Batch Screen
# Given I log in to BCSS "England" as user role "HubManager"
# When I view the active batch list
# And I select an active batch
# Then I view the details of an active batch

# # Copied from the now-deleted UserPathway.feature - need to tidy up duplicate steps etc
# # rovi ignored as this contains non implemented steps.
# @ignore
# Scenario: User prints the Pre-Invitation Letters batch (#4)
# Given I log in to BCSS "England" as user role "Hub Manager - State Registered"
# When I navigate to the Communications Production > Active Batch List Page
#     And I prepare the Pre-Invitation FIT letter batch
# Then The Pre-Invitation FIT letter batch is no longer listed

@pytest.mark.regression
def test_headings_on_active_batch_list_screen(page: Page) -> None:
    """
    Confirms that the active batch list table contains a sortable and filterable column for "ID", "Type", "Original",
    "Event Code", "Description", "Batch Split By", "Screening Centre", "Status", "Priority", "Deadline" and "Count"
    """
    # Scenario: Check headings on Active Batch List Screen
    # Given I log in to BCSS "England" as user role "HubManager"
    # When I view the active batch list
    # Then the table contains a sortable and filterable column for "ID"
    # And the table contains a sortable and filterable column for "Type"
    # And the table contains a sortable and filterable column for "Original"
    # And the table contains a sortable and filterable column for "Event Code"
    # And the table contains a sortable and filterable column for "Description"
    # And the table contains a sortable and filterable column for "Batch Split By"
    # And the table contains a sortable and filterable column for "Screening Centre"
    # And the table contains a sortable and filterable column for "Status"
    # And the table contains a sortable and filterable column for "Priority"
    # And the table contains a sortable and filterable column for "Deadline"
    # And the table contains a sortable and filterable column for "Count"
    batch_list_page = ActiveBatchListPage(page)
    # 🔍 TEMPORARY DEBUGGING
    table = TableUtils(page, "table.active-batch-list")
    print("DEBUG - Headers Found:", table.get_table_headers())
    batch_list_page.verify_sortable_and_filterable_columns()
