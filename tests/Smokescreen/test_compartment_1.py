import pytest
from pypdf import PdfReader
from playwright.sync_api import Page, expect
import pandas as pd
import os
from my_pages import *

# To Do:
# Create more POMs
# Add more fail states
# Add more logging to understand what is going on
# Convert import pages * into 1 line
# Move functions to utils
# Remove as many hard coded timeouts as possible
# Create a generic click() function -> this aims to solve an issue where sometimes it thinks it has clicked the element but the page does not change

@pytest.mark.wip
def test_example(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user_bcss401()

    # Create plan
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_planning_and_monitoring_page()
    InvitationsMonitoring(page).go_to_bcss001_invitations_plan_page()
    InvitationsPlans(page).go_to_create_a_plan_page()
    CreateAPlan(page).click_set_all_button()
    CreateAPlan(page).fill_daily_invitation_rate_field("1")
    CreateAPlan(page).click_update_button()
    CreateAPlan(page).click_confirm_button()
    CreateAPlan(page).click_save_button()
    CreateAPlan(page).fill_note_field("test data")
    CreateAPlan(page).click_saveNote_button()
    expect(page).to_have_url("https://bcss-bcss-18680-ddc-bcss.k8s-nonprod.texasplatform.uk/invitation/plan/23159/23162/")

    # Generate Invitations
    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_generate_invitations_page()
    GenerateInvitations(page).click_generate_invitations_button()
    GenerateInvitations(page).wait_for_invitation_generation_complete()

    # Print the batch of Pre-Invitation Letters
    batch_processing(page, "S1", "Pre-invitation (FIT)", "S9 - Pre-invitation Sent")
    batch_processing(page, "S1", "Pre-invitation (FIT) (digital leaflet)", "S9 - Pre-invitation Sent")

    database_connection_exec("bcss_timed_events")

    # Print the batch of Invitation & Test Kit Letters
    batch_processing(page, "S9", "Invitation & Test Kit (FIT)", "S10 - Invitation & Test Kit Sent")

    # Print a set of reminder letters
    batch_processing(page, "S10", "Test Kit Reminder", "S19 - Reminder of Initial Test Sent")

    # Log out
    NavigationBar(page).click_log_out_link()
    expect(page.get_by_role("heading", name="You have logged out")).to_be_visible()

def batch_processing(page: Page, batch_type: str, batch_description: str, latest_event_status: str):
    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_communications_production_page()
    CommunicationsProduction(page).go_to_active_batch_list_page()
    ActiveBatchList(page).enter_event_code_filter(batch_type)

    batch_description_cells = page.locator(f"//td[text()='{batch_description}']")

    if batch_description_cells.count() == 0 and batch_description == "Pre-invitation (FIT) (digital leaflet)":
        print(f"No S1 Pre-invitation (FIT) (digital leaflet) batch found. Skipping to next step")
        return
    elif batch_description_cells.count() == 0 and page.locator("td", has_text="No matching records found"):
        pytest.fail(f"No {batch_type} {batch_description} batch found")

    for i in range(batch_description_cells.count()):
        row = batch_description_cells.nth(i).locator("..")  # Get the parent row

        # Check if the row contains "Prepared" or "Open"
        if row.locator("td", has_text="Prepared").count() > 0 or row.locator("td", has_text="Open").count() > 0:
            # Find the first link in that row and click it
            link = row.locator("a").first
            link_text = link.inner_text()  # Get the batch id dynamically
            link.click()
            break
        else:
            pytest.fail(f"No open/prepared '{batch_type} - {batch_description}' batch found")

    ManageActiveBatch(page).click_prepare_button()

    ManageActiveBatch(page).reprepare_batch_text.wait_for()

    # This loops through each Retrieve button and clicks each one
    retrieve_button_count = 0
    for retrieve_button in range (ManageActiveBatch(page).retrieve_button.count()):
        retrieve_button_count += 1
        # Start waiting for the pdf download
        with page.expect_download() as download_info:
            # Perform the action that initiates download
            ManageActiveBatch(page).retrieve_button.nth(retrieve_button-1).click()
        download_file = download_info.value
        file = download_file.suggested_filename
        # Wait for the download process to complete and save the downloaded file in a temp folder
        download_file.save_as(file)
        if file.endswith(".pdf"):
            nhs_no = pdf_Reader(file)
            os.remove(file) # Deletes the file after extracting the necessary data
        elif file.endswith(".csv"):
            # csv_df = csv_Reader(file) # Currently no use in compartment 1, will be necessary for future compartments
            os.remove(file) # Deletes the file after extracting the necessary data

    # This loops through each Confirm printed button and clicks each one
    for _ in range (retrieve_button_count):
        page.on("dialog", lambda dialog: dialog.accept())
        ManageActiveBatch(page).confirm_button.nth(0).click()

    page.locator('text="Batch Successfully Archived and Printed"').wait_for()

    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_communications_production_page()
    CommunicationsProduction(page).go_to_archived_batch_list_page()
    ArchivedBatchList(page).enter_id_filter(link_text)
    expect(page.locator("td").filter(has_text=link_text)).to_be_visible() # Checks to see if the batch is now archived

    subject_search_by_nhs_no(page, nhs_no, latest_event_status)

def pdf_Reader(file: str):
    reader = PdfReader(file)

    # For loop looping through all pages of the file to find the NHS Number
    for pages in reader.pages:
        text = pages.extract_text()
        if "NHS No" in text:
            # If NHS number is found split the text by every new line into a list
            text = text.splitlines(True)
            for split_text in text:
                if "NHS No" in split_text:
                    # If a string is found containing "NHS No" only digits are stored into nhs_no
                    nhs_no = "".join([ele for ele in split_text if ele.isdigit()])
                    break
    return nhs_no

def csv_Reader(file: str):
    csv_df = pd.read_csv(file)
    return csv_df

def subject_search_by_nhs_no(page: Page, nhs_no: str, latest_event_status: str):
    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_screening_subject_search_page()
    SubjectScreeningPage(page).click_nhs_number_filter()
    SubjectScreeningPage(page).nhs_number_filter.fill(nhs_no)
    SubjectScreeningPage(page).nhs_number_filter.press("Enter")
    SubjectScreeningPage(page).click_search_button()
    expect(page.get_by_role("cell", name="Subject Screening Summary", exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name="Latest Event Status", exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name=latest_event_status, exact=True)).to_be_visible()
