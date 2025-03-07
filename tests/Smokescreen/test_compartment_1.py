import pytest
from playwright.sync_api import Page
from my_pages import *
from utils.batch_processing import batch_processing
from utils.oracle import OracleDB

# To Do:
# Create a common click() function -> this aims to solve an issue where sometimes it thinks it has clicked the element but the page does not change
# playwright._impl._errors.Error: Dialog.accept: Cannot accept dialog which is already handled! - Have a look at removing this error (probably from line 67 of batch_processing)

@pytest.mark.wip
def test_compartment_1(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user("BCSS401")

    # Create plan
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_planning_and_monitoring_page()
    InvitationsMonitoring(page).go_to_bcss001_invitations_plan_page()
    InvitationsPlans(page).go_to_create_a_plan_page()
    CreateAPlan(page).click_set_all_button()
    CreateAPlan(page).fill_daily_invitation_rate_field("10")
    CreateAPlan(page).click_update_button()
    CreateAPlan(page).click_confirm_button()
    CreateAPlan(page).click_save_button()
    CreateAPlan(page).fill_note_field("test data")
    CreateAPlan(page).click_saveNote_button()
    InvitationsPlans(page).invitations_plans_title.wait_for()

    # Generate Invitations
    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_generate_invitations_page()
    GenerateInvitations(page).click_generate_invitations_button()
    GenerateInvitations(page).wait_for_invitation_generation_complete()

    # Print the batch of Pre-Invitation Letters
    s1_nhs_numbers = batch_processing(page, "S1", "Pre-invitation (FIT)", "S9 - Pre-invitation Sent")
    batch_processing(page, "S1", "Pre-invitation (FIT) (digital leaflet)", "S9 - Pre-invitation Sent")
    for nhs_no in range(len(s1_nhs_numbers)):
        OracleDB().exec_bcss_timed_events(s1_nhs_numbers[nhs_no-1])

    # Print the batch of Invitation & Test Kit Letters
    s9_nhs_numbers = batch_processing(page, "S9", "Invitation & Test Kit (FIT)", "S10 - Invitation & Test Kit Sent")
    for nhs_no in range(len(s9_nhs_numbers)):
        OracleDB().exec_bcss_timed_events(s9_nhs_numbers[nhs_no-1])

    # Print a set of reminder letters
    batch_processing(page, "S10", "Test Kit Reminder", "S19 - Reminder of Initial Test Sent")

    # Log out
    NavigationBar(page).click_log_out_link()
    Logout(page).verify_log_out_page()
    page.close()
