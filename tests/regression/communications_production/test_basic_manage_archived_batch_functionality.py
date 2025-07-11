import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.communication_production.communications_production_page import (
    CommunicationsProductionPage,
)
from pages.communication_production.batch_list_page import ArchivedBatchListPage
from utils.user_tools import UserTools
from pages.communication_production.manage_active_batch_page import (
    ManageActiveBatchPage,
)
from pages.communication_production.manage_archived_batch_page import (
    ManageArchivedBatchPage,
)
from pages.communication_production.letter_library_index_page import (
    LetterLibraryIndexPage,
)
from pages.communication_production import letter_library_index_page
from utils.batch_processing import prepare_and_print_batch


@pytest.fixture
def select_user(page: Page):
    def _login_as(user_role: str):
        # Log in with the specified user
        UserTools.user_login(page, user_role)
        # Navigate to communications production page
        BasePage(page).go_to_communications_production_page()
        return page

    return _login_as


@pytest.mark.letters_tests
@pytest.mark.regression
def test_reprint_and_archive_letter_batch(select_user) -> None:
    """
    Scenario: I can take an archived batch, reprint it, then archive that new batch
    Given I log in to BCSS "England" as user role "HubManagerStateRegistered"
    When I view the archived batch list
    And I view the "Original" type archived letter batch for "S1" "Pre"
    And I reprint the archived letter batch
    And I prepare the letter batch
    And I retrieve and confirm the letters
    And my batch is now archived
    """
    # Step 1: Log in as user and navigate to Archived Batch List
    page = select_user("Hub Manager State Registered at BCS01")
    CommunicationsProductionPage(page).go_to_archived_batch_list_page()
    batch_list_page = ArchivedBatchListPage(page)

    # Step 2: Ensure the archived batch list table is visible
    batch_list_page.assert_batch_table_visible()
    # Wait for at least one row to appear
    page.wait_for_function(
        "document.querySelectorAll('table#batchList tbody tr').length > 1", timeout=8000
    )
    rows = page.locator("table#batchList tbody tr")
    row_count = rows.count()

    for i in range(row_count):
        row = rows.nth(i)

    # Step 3: Find and open archived batch with Type "Original", Event Code "S1", and Description "Pre"
    # You might want to use filters like:
    row = batch_list_page.get_archived_batch_row(
        "Original", "S1", "Pre-invitation (FIT)"
    )
    if not row:
        pytest.skip("No archived 'Original' S1 Pre batches found to reprint.")

    batch_id = row.locator("a").first.inner_text()
    row.locator("a").first.click()

    # Step 4: Perform reprint from Archived Batch detail screen
    manage_archived_page = ManageArchivedBatchPage(page)  # Assuming reuse
    manage_archived_page.assert_archived_batch_details_visible()
    manage_archived_page.click_reprint_button()
    BasePage(page).safe_accept_dialog(page.get_by_role("button", name="Reprint Batch"))

    # Step 5: Wait for navigation to new Active Batch screen
    # You’ll likely land back in Active Batch context
    manage_active_page = ManageActiveBatchPage(page)
    manage_active_page.assert_active_batch_details_visible()

    # Step 6: Prepare, retrieve and confirm new batch
    prepare_and_print_batch(page, link_text=batch_id)

    # Step 7: Assert batch archived successfully
    manage_archived_page.confirm_archived_message_visible()


@pytest.mark.wip
@pytest.mark.letters_tests
@pytest.mark.regression
def test_check_that_s1_has_supplementary_batches(select_user) -> None:
    """
    Scenario: I can create a supplementary batch for S1 and archive it
    Given I log in to BCSS "England" as user role "HubManagerStateRegistered"
    When I view the letter library index
    And I filter the letter library index list to view the "Supplementary Letters" letters group
    And I ensure that I can create "S1" supplementary batches
    And I view the archived batch list
    And I view the "Original" type archived letter batch for "S1" "Pre"
    And I create a supplementary batch
    And I prepare the letter batch
    And I retrieve and confirm the letters
    And my batch is now archived
    """
    # Step 1: Log in as user and navigate to Letter Library Index
    page = select_user("Hub Manager State Registered at BCS01")
    CommunicationsProductionPage(page).go_to_letter_library_index_page()

    # Step 2: Filter for "Supplementary Letters" group
    LetterLibraryIndexPage(page).filter_by_letters_group("Supplementary Letters")

    # TODO: Is this below step required? There is no button to create a supplementary batch in the letter library index page.
    # and there are no supplementary letters in the letter library index page.

    # Step 3: Ensure S1 supplementary batches can be created
    if not letter_library_index_page.can_create_supplementary_batches("S1"):
        pytest.skip("No S1 supplementary batches available for creation.")

    # Step 4: Navigate to Archived Batch List
    archived_batch_list_page = ArchivedBatchListPage(page)
    archived_batch_list_page.assert_batch_table_visible()

    # Step 5: Find and open archived batch with Type "Original", Event Code "S1", and Description "Pre"
    row = archived_batch_list_page.get_archived_batch_row(
        "Original", "S1", "Pre-invitation (FIT)"
    )
    if not row:
        pytest.skip("No archived 'Original' S1 Pre batches found to reprint.")

    batch_id = row.locator("a").first.inner_text()
    row.locator("a").first.click()

    # Step 6: Create a supplementary batch
    manage_active_page = ManageActiveBatchPage(page)
    manage_active_page.click_prepare_button()

    # Step 7: Prepare the letter batch
    manage_active_page.prepare_and_print()

    # Step 8: Retrieve and confirm letters
    manage_active_page.retrieve_and_confirm_letters()

    # Step 9: Confirm the batch is now archived
    manage_archived_page = ManageArchivedBatchPage(page)
    manage_archived_page.confirm_archived_message_visible()
