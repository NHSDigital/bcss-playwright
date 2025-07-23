import pytest
import logging
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.user_tools import UserTools
from pages.communication_production.communications_production_page import (
    CommunicationsProductionPage,
)
from pages.communication_production.letter_library_index_page import (
    LetterLibraryIndexPage,
    LetterDefinitionDetailPage,
)

# @BCSSAdditionalTests @LettersTests
# Feature: Letter Library

# Narrative Description: As a user of BCSS I am able to view national letter definitions,
# and create local versions

# # Notes: In the Letter Library Index, when you click on a LETTER code, this takes you to the Version History
# # screen.  When you click on a CSV code, this takes you to the CSV File Format screen.

# -------------------------------------------------------------------------------------------------
#   S83f : FIT self-referral letters:
# 	S83f-ATT = pre-invitation letter
# 	S83f = invitation letter
# 	S83f-CSV = test kit details
# -------------------------------------------------------------------------------------------------


@pytest.fixture
def select_user(page: Page):
    def _login_as(user_role: str):
        # Log in with the specified user
        UserTools.user_login(page, user_role)
        # Navigate to call and recall page
        BasePage(page).go_to_call_and_recall_page()
        return page

    return _login_as

@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.letters_tests
def test_all_s83f_letter_parts_are_listed_in_letter_library(select_user) -> None:
    """
    Scenario: All three parts of the S83f letter exist
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the letter library index
    And I filter the letter library index list to view the "Invitation Letters" letters group
    Then the "S83f" letter is listed in the letter library index
    And the "S83f-CSV" letter is listed in the letter library index
    And the "S83f-ATT" letter is listed in the letter library index
    """
    logging.info(
        "[TEST START] Verify all parts of the S83f letter exist in Letter Library"
    )
    user_role = "Hub Manager at BCS01"

    # Step 1: Log in and land on Call and Recall page
    page = select_user(user_role)
    logging.info(f"[LOGIN] Logged in as {user_role}")

    # Step 2: Navigate to Letter Library Index
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_letter_library_index_page()
    logging.info("[NAVIGATION] Navigated to Letter Library Index page")

    # Step 3: Apply filter
    letter_index_page = LetterLibraryIndexPage(page)
    letter_index_page.filter_by_letters_group("Invitation Letters")
    letter_index_page.verify_letter_library_index_title()
    logging.info("[FILTER] Applied 'Invitation Letters' group filter")

    # Step 4: Assert that all required letter codes are visible
    expected_codes = ["S83f", "S83f-CSV", "S83f-ATT"]
    for code in expected_codes:
        matching_row = letter_index_page.table_utils.get_row_where({"Code": code})
        assert (
            matching_row is not None
        ), f"[ASSERTION FAILED] Letter code '{code}' not found"
        logging.info(f"[ASSERTION PASSED] Letter code '{code}' listed in library")


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.letters_tests
def test_s83f_letter_definition_has_correct_settings(select_user) -> None:
    """
    Scenario: A current S83f FIT self-referral invitation and test kit letter exists and has the correct settings
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the letter library index
    And I view the "S83f" letter definition
    Then the letter definition setting "Description" is "Invitation & Test Kit (Self-referral) (FIT)"
    And the letter definition setting "Letter Code" is "S83f"
    And the letter definition setting "Letter Group" is "Invitation Letters"
    And the letter definition setting "Letter Format" is "PDF-A4-V03"
    And the letter definition setting "Priority" is "High"
    And the letter definition setting "Destination" is "Patient"
    And the letter definition setting "Event Status" is "S83"
    And there "is" a current version of the selected letter definition
    """
    logging.info("[TEST START] Verify S83f letter definition has correct settings")
    user_role = "Hub Manager at BCS01"

    # Step 1: Log in and navigate to Letter Library
    page = select_user(user_role)
    logging.info(f"[LOGIN] Logged in as {user_role}")
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_letter_library_index_page()
    logging.info("[NAVIGATION] Navigated to Letter Library Index page")

    # Step 2: Filter and open S83f letter definition
    letter_index_page = LetterLibraryIndexPage(page)
    letter_index_page.filter_by_letters_group("Invitation Letters")
    letter_index_page.verify_letter_library_index_title()

    letter_row = letter_index_page.table_utils.get_row_where({"Code": "S83f"})
    assert letter_row is not None, "[ASSERTION FAILED] S83f letter not found"
    letter_row.locator("a").click()
    logging.info("[ACTION] Opened S83f letter definition")

    # Step 3: Assert letter settings
    letter_detail_page = LetterDefinitionDetailPage(page)
    letter_detail_page.assert_definition_setting(
        "Description", "Invitation & Test Kit (Self-referral) (FIT)"
    )
    letter_detail_page.assert_definition_setting("Letter Code", "S83f")
    letter_detail_page.assert_definition_setting("Letter Group", "Invitation Letters")
    letter_detail_page.assert_definition_setting("Letter Format", "PDF-A4-V03")
    letter_detail_page.assert_definition_setting("Priority", "High")
    letter_detail_page.assert_definition_setting("Destination", "Patient")
    letter_detail_page.assert_definition_setting("Event Status", "S83")
    logging.info("[ASSERTION PASSED] All letter settings match expected values")

    # Step 4: Confirm current version exists
    assert (
        letter_detail_page.has_current_version()
    ), "[ASSERTION FAILED] No current version for S83f"
    logging.info("[ASSERTION PASSED] S83f has a current version")


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.letters_tests
def test_s83f_att_letter_definition_has_correct_settings(select_user) -> None:
    """
    Scenario: A current S83f-ATT FIT self-referral pre-invitation letter exists and has the correct settings
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the letter library index
    And I view the "S83f-ATT" letter definition
    And I pause to admire the view for "0" seconds
    Then the letter definition setting "Description" is "Pre-invitation (Self-referral) (FIT)"
    And the letter definition setting "Letter Code" is "S83f-ATT"
    And the letter definition setting "Letter Group" is "Invitation Letters"
    And the letter definition setting "Letter Format" is "PDF-A4-V03"
    And the letter definition setting "Priority" is "High"
    And the letter definition setting "Destination" is "Patient"
    And the letter definition setting "Event Status" is "S83"
    And there "is" a current version of the selected letter definition
    """
    logging.info("[TEST START] Verify S83f-ATT letter definition has correct settings")
    user_role = "Hub Manager at BCS01"

    # Step 1: Log in and navigate to Letter Library Index
    page = select_user(user_role)
    logging.info(f"[LOGIN] Logged in as {user_role}")
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_letter_library_index_page()
    logging.info("[NAVIGATION] Navigated to Letter Library Index page")

    # Step 2: Filter and open S83f-ATT letter definition
    letter_index_page = LetterLibraryIndexPage(page)
    letter_index_page.filter_by_letters_group("Invitation Letters")
    letter_index_page.verify_letter_library_index_title()

    letter_row = letter_index_page.table_utils.get_row_where({"Code": "S83f-ATT"})
    assert letter_row is not None, "[ASSERTION FAILED] S83f-ATT letter not found"
    letter_row.locator("a").click()
    logging.info("[ACTION] Opened S83f-ATT letter definition")

    # Step 3: Pause to admire the view
    page.wait_for_timeout(1000)

    # Step 4: Assert all settings
    letter_detail_page = LetterDefinitionDetailPage(page)
    letter_detail_page.assert_definition_setting(
        "Description", "Pre-invitation (Self-referral) (FIT)"
    )
    letter_detail_page.assert_definition_setting("Letter Code", "S83f-ATT")
    letter_detail_page.assert_definition_setting("Letter Group", "Invitation Letters")
    letter_detail_page.assert_definition_setting("Letter Format", "PDF-A4-V03")
    letter_detail_page.assert_definition_setting("Priority", "High")
    letter_detail_page.assert_definition_setting("Destination", "Patient")
    letter_detail_page.assert_definition_setting("Event Status", "S83")
    logging.info("[ASSERTION PASSED] All S83f-ATT letter settings match expectations")

    # Step 5: Confirm current version exists
    assert (
        letter_detail_page.has_current_version()
    ), "[ASSERTION FAILED] No current version for S83f-ATT"
    logging.info("[ASSERTION PASSED] S83f-ATT has a current version")


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.letters_tests
def test_s83f_define_local_letter_reuses_existing_settings(select_user) -> None:
    """
    Scenario: As a hub manager, I can safely access and submit the local letter definition flow for S83f
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the letter library index
    And I view the "S83f" letter definition
    Then I submit the local letter definition form using values that match the existing letter settings

    Note: Rather than checking for an existing local version, we have removed the data dependency
    so that we can always test the functionality
    """
    logging.info("[TEST START] Define local version of S83f without altering data")

    user_role = "Hub Manager at BCS01"
    page = select_user(user_role)
    logging.info(f"[LOGIN] Logged in as {user_role}")

    # Step 1: Navigate to Letter Library Index
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_letter_library_index_page()

    letter_index_page = LetterLibraryIndexPage(page)
    letter_index_page.filter_by_letters_group("Invitation Letters")

    letter_row = letter_index_page.table_utils.get_row_where({"Code": "S83f"})
    assert letter_row is not None, "[ASSERTION FAILED] S83f letter not found"
    letter_row.locator("a").click()

    page.wait_for_timeout(1000)

    # Step 2: Define Local Version using known-good settings
    letter_index_page.click_define_supplementary_letter_button()
    letter_index_page.define_supplementary_letter(
        description="Invitation & Test Kit (Self-referral) (FIT)",
        destination_id="12057",  # Patient
        priority_id="12016",  # High
        signatory="Dr Hub",
        job_title="Hub Manager",
        paragraph_text="Invitation and test kit details as per S83f standard.",
    )
    logging.info("[ACTION] Local definition form submitted with existing settings")


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.letters_tests
def test_s83f_att_define_local_letter_reuses_existing_settings(select_user) -> None:
    """
    Scenario: As a hub manager, I can safely access and submit the local letter definition flow for S83f-ATT
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the letter library index
    And I view the "S83f-ATT" letter definition
    Then I submit the local letter definition form using values that match the existing letter settings

    Note: Rather than checking for an existing local version, we have removed the data dependency
    so that we can always test the functionality
    """
    logging.info("[TEST START] Define local version of S83f-ATT without altering data")

    user_role = "Hub Manager at BCS01"
    page = select_user(user_role)
    logging.info(f"[LOGIN] Logged in as {user_role}")

    # Step 1: Navigate to Letter Library Index
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_letter_library_index_page()

    letter_index_page = LetterLibraryIndexPage(page)
    letter_index_page.filter_by_letters_group("Invitation Letters")

    letter_row = letter_index_page.table_utils.get_row_where({"Code": "S83f-ATT"})
    assert letter_row is not None, "[ASSERTION FAILED] S83f-ATT letter not found"
    letter_row.locator("a").click()

    page.wait_for_timeout(1000)

    # Step 2: Define Local Version using known-good settings
    letter_index_page.click_define_supplementary_letter_button()
    letter_index_page.define_supplementary_letter(
        description="Pre-invitation (Self-referral) (FIT)",
        destination_id="12057",  # Patient
        priority_id="12016",  # High
        signatory="Dr Hub",
        job_title="Hub Manager",
        paragraph_text="Pre-invitation details as per S83f-ATT standard.",
    )
    logging.info("[ACTION] Local definition form submitted with existing settings")


# # Manual Scenario: I set up a local version for S83f-ATT pre-invitation letter
# # Given I log in to BCSS England as user role Hub Manager
# # When I view the letter library index
# # And I view the S83f-ATT pre-invitation letter definition
# # Then I define a local version

# #-------------------------------------------------------------------------------------------------
# # A183 : 1st Positive Appointment Requested letter


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.letters_tests
def test_a183_letter_definition_has_correct_settings(select_user) -> None:
    """
    Scenario: A current A183 letter exists and has the correct settings
    Given I log in to BCSS "England" as user role "HubManager"
    When I view the letter library index
    And I view the "A183" letter definition
    And I pause to admire the view for "0" seconds
    Then the letter definition setting "Description" is "Practitioner Clinic 1st Appointment"
    And the letter definition setting "Letter Code" is "A183"
    And the letter definition setting "Letter Group" is "Practitioner Clinic Letters"
    And the letter definition setting "Letter Format" is "PDF-A4-V03"
    And the letter definition setting "Priority" is "Urgent"
    And the letter definition setting "Destination" is "Patient"
    And the letter definition setting "Event Status" is "A183"
    And there "is" a current version of the selected letter definition
    """
    logging.info("[TEST START] Verify A183 letter definition has correct settings")
    user_role = "Hub Manager at BCS01"

    # Step 1: Login and navigate
    page = select_user(user_role)
    logging.info(f"[LOGIN] Logged in as {user_role}")
    base_page = BasePage(page)
    base_page.click_main_menu_link()
    base_page.go_to_communications_production_page()
    CommunicationsProductionPage(page).go_to_letter_library_index_page()
    logging.info("[NAVIGATION] Reached Letter Library Index")

    # Step 2: Filter and open A183 letter
    letter_index_page = LetterLibraryIndexPage(page)
    letter_index_page.filter_by_letters_group("Practitioner Clinic Letters")
    letter_index_page.verify_letter_library_index_title()

    letter_row = letter_index_page.table_utils.get_row_where({"Code": "A183"})
    assert letter_row is not None, "[ASSERTION FAILED] A183 letter not listed"
    letter_row.locator("a").click()
    logging.info("[ACTION] Opened A183 letter definition")

    # Step 3: Pause and assert settings
    page.wait_for_timeout(1000)
    letter_detail_page = LetterDefinitionDetailPage(page)
    letter_detail_page.assert_definition_setting(
        "Description", "Practitioner Clinic 1st Appointment"
    )
    letter_detail_page.assert_definition_setting("Letter Code", "A183")
    letter_detail_page.assert_definition_setting(
        "Letter Group", "Practitioner Clinic Letters"
    )
    letter_detail_page.assert_definition_setting("Letter Format", "PDF-A4-V03")
    letter_detail_page.assert_definition_setting("Priority", "Urgent")
    letter_detail_page.assert_definition_setting("Destination", "Patient")
    letter_detail_page.assert_definition_setting("Event Status", "A183")
    logging.info("[ASSERTION PASSED] All A183 letter settings verified")

    # Step 4: Confirm current version exists
    assert (
        letter_detail_page.has_current_version()
    ), "[ASSERTION FAILED] No current version for A183"
    logging.info("[ASSERTION PASSED] A183 has a current version")
