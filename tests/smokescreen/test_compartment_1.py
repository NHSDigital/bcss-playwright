import pytest
import logging
from pages.logout.log_out_page import LogoutPage
from utils.user_tools import UserTools
from pages.base_page import BasePage
from pages.call_and_recall.call_and_recall_page import CallAndRecallPage
from pages.call_and_recall.invitations_monitoring_page import InvitationsMonitoringPage
from pages.call_and_recall.invitations_plans_page import InvitationsPlansPage
from pages.call_and_recall.create_a_plan_page import CreateAPlanPage
from pages.call_and_recall.generate_invitations_page import GenerateInvitationsPage
from playwright.sync_api import Page
from utils.batch_processing import batch_processing


@pytest.mark.smokescreen
@pytest.mark.compartment1
@pytest.mark.compartment1_plan_creation
def test_create_invitations_plan(page: Page, smokescreen_properties: dict) -> None:
    """
    This is used to create the invitations plan. As it is not always needed it is separate to the main Compartment 1 function
    """
    logging.info("Compartment 1 - Create Invitations Plan")
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
    # Create plan - England
    BasePage(page).go_to_call_and_recall_page()
    CallAndRecallPage(page).go_to_planning_and_monitoring_page()
    InvitationsMonitoringPage(page).go_to_invitation_plan_page(
        smokescreen_properties["c1_screening_centre_code"]
    )
    InvitationsPlansPage(page).go_to_create_a_plan_page()
    logging.info("Setting daily invitation rate")
    CreateAPlanPage(page).click_set_all_button()
    CreateAPlanPage(page).fill_daily_invitation_rate_field(
        smokescreen_properties["c1_daily_invitation_rate"]
    )
    CreateAPlanPage(page).click_update_button()
    CreateAPlanPage(page).click_confirm_button()
    CreateAPlanPage(page).click_save_button()
    CreateAPlanPage(page).fill_note_field("test data")
    CreateAPlanPage(page).click_save_note_button()
    InvitationsPlansPage(page).invitations_plans_title.wait_for()
    logging.info("Invitation plan created")


@pytest.mark.vpn_required
@pytest.mark.smokescreen
@pytest.mark.compartment1
def test_compartment_1(page: Page, smokescreen_properties: dict) -> None:
    """
    This is the main compartment 1 function. It covers the following:
    - Generating invitations based on the invitation plan
    - Processes S1 (FIT) batches
    - Processes S9 (FIT) batches
    - Processes S10 (FIT) batches
    """
    logging.info("Compartment 1 - Generate Invitations")
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Generate Invitations
    BasePage(page).go_to_call_and_recall_page()
    CallAndRecallPage(page).go_to_generate_invitations_page()
    logging.info("Generating invitations based on the invitations plan")
    GenerateInvitationsPage(page).click_generate_invitations_button()
    self_referrals_available = GenerateInvitationsPage(
        page
    ).wait_for_invitation_generation_complete(
        int(smokescreen_properties["c1_daily_invitation_rate"])
    )

    # Print the batch of Pre-Invitation Letters - England
    logging.info("Compartment 1 - Process S1 Batch")
    if self_referrals_available:
        batch_processing(
            page,
            "S1",
            "Pre-invitation (FIT) (digital leaflet)",
            "S9 - Pre-invitation Sent",
        )
    else:
        logging.warning(
            "Skipping S1 Pre-invitation (FIT) (digital leaflet) as no self referral invitations were generated"
        )
    batch_processing(
        page, "S1", "Pre-invitation (FIT)", "S9 - Pre-invitation Sent", True, True
    )

    # Print the batch of Invitation & Test Kit Letters - England
    logging.info("Compartment 1 - Process S9 Batch")
    batch_processing(
        page,
        "S9",
        "Invitation & Test Kit (FIT)",
        "S10 - Invitation & Test Kit Sent",
        True,
    )

    # Print a set of reminder letters
    logging.info("Compartment 1 - Process S10 Batch")
    batch_processing(
        page, "S10", "Test Kit Reminder", "S19 - Reminder of Initial Test Sent"
    )

    # Log out
    LogoutPage(page).log_out()
