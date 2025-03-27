import pytest
from playwright.sync_api import Page
from my_pages import *
from utils.batch_processing import batch_processing
from utils.oracle import OracleDB

@pytest.mark.smoke
@pytest.mark.compartment1
def test_create_invitations_plan(page: Page) -> None:
    logging.info("Compartment 1 - Create Invitations Plan")
    UserTools.user_login(page, "Hub Manager State Registered")
    # Create plan - England
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_planning_and_monitoring_page()
    InvitationsMonitoring(page).go_to_bcss001_invitations_plan_page()
    InvitationsPlans(page).go_to_create_a_plan_page()
    logging.info("Setting daily invitation rate")
    CreateAPlan(page).click_set_all_button()
    CreateAPlan(page).fill_daily_invitation_rate_field("10")
    CreateAPlan(page).click_update_button()
    CreateAPlan(page).click_confirm_button()
    CreateAPlan(page).click_save_button()
    CreateAPlan(page).fill_note_field("test data")
    CreateAPlan(page).click_save_note_button()
    InvitationsPlans(page).invitations_plans_title.wait_for()
    logging.info("Invitation plan created")

@pytest.mark.smoke
@pytest.mark.smokescreen
@pytest.mark.compartment1
def test_compartment_1(page: Page) -> None:
    logging.info("Compartment 1 - Generate Invitations")
    UserTools.user_login(page, "Hub Manager State Registered")

    # Generate Invitations
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_generate_invitations_page()
    logging.info("Generating invitations based on the invitations plan")
    GenerateInvitations(page).click_generate_invitations_button()
    GenerateInvitations(page).wait_for_invitation_generation_complete()

    # Print the batch of Pre-Invitation Letters - England
    logging.info("Compartment 1 - Process S1 Batch")
    batch_processing(page, "S1", "Pre-invitation (FIT) (digital leaflet)", "S9 - Pre-invitation Sent")
    nhs_number_df = batch_processing(page, "S1", "Pre-invitation (FIT)", "S9 - Pre-invitation Sent")
    OracleDB().exec_bcss_timed_events(nhs_number_df)

    # Print the batch of Invitation & Test Kit Letters - England
    logging.info("Compartment 1 - Process S9 Batch")
    nhs_number_df = batch_processing(page, "S9", "Invitation & Test Kit (FIT)", "S10 - Invitation & Test Kit Sent")
    OracleDB().exec_bcss_timed_events(nhs_number_df)

    # Print a set of reminder letters
    logging.info("Compartment 1 - Process S10 Batch")
    batch_processing(page, "S10", "Test Kit Reminder", "S19 - Reminder of Initial Test Sent")

    # Log out
    Logout(page).log_out()