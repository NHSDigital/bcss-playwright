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
from utils.batch_processing import prepare_and_print_batch


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
def test_prepare_retrieve_and_confirm_active_letter_batch(select_user) -> None:
    """
    Scenario: I can prepare, retrieve and confirm a letter batch of any number of files
    Given I log in to BCSS "England" as user role "HubManagerStateRegistered"
    When I view the active batch list
    And there are open letter batches to process in the active batch list
    Then I view the "Original" type "Open" status active letter batch
    And I prepare the letter batch
    And I retrieve and confirm the letters
    """
    # Step 1: Log in as Hub Manager (State Registered) and access Active Batch List
    page = select_user("Hub Manager State Registered at BCS01")
    batch_list_page = ActiveBatchListPage(page)

    # Step 2: Ensure the active batch list table is visible
    batch_list_page.assert_batch_table_visible()

    # Step 3: Locate the first batch with type "Original" and status "Open"
    row = batch_list_page.get_open_original_batch_row()
    if not row:
        pytest.skip("No open 'Original' batches found in the active batch list.")

    # Step 4: Capture the batch ID from the selected row and click to open
    batch_id = row.locator("a").first.inner_text()
    row.locator("a").first.click()

    # Step 5: Assert that Manage Active Batch page has loaded
    manage_page = ManageActiveBatchPage(page)
    manage_page.assert_active_batch_details_visible()

    # Step 6: Prepare, retrieve and confirm the batch using utility method
    prepare_and_print_batch(page, link_text=batch_id)
