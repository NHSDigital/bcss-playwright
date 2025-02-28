import pytest
from pypdf import PdfReader
from playwright.sync_api import Page, expect
import pandas as pd
import os
import sys
sys.path.append("../")
from utils.oracle import *
from pages.bcss_home_page import *
from pages.login_page import *
from pages.communications_production_page import *
from pages.call_and_recall_page import *
from pages.active_batch_list_page import *
from pages.archived_batch_list_page import *
from pages.navigation_bar_links import *
from pages.subject_screening_page import *

# @pytest.mark.wip2 # Not working at the moment
# def test_prereq():
#     database_connection_exec("prereq_check")

#     paramater_32 = database_connection_query("select DEFAULT_VALUE from PARAMETERS where PARAM_ID = 32")
#     print(f"paramater_32: {paramater_32}")
#     if paramater_32[0] != "-1":
#         database_connection_query("UPDATE PARAMETERS SET DEFAULT_VALUE = -1 WHERE PARAM_ID = 32")
#         database_connection_query("COMMIT")
#     paramater_31 = database_connection_query("select DEFAULT_VALUE from PARAMETERS where PARAM_ID = 31")
#     print(f"paramater_31: {paramater_31}")
#     if paramater_31[0] != "-1":
#         database_connection_query("UPDATE PARAMETERS SET DEFAULT_VALUE = -1 WHERE PARAM_ID = 31")
#         database_connection_query("COMMIT")


# To Do:
# Create more POM
# Remove as many hard coded timeouts as possible
# Add more fail states
# Add more logging to understand what is going on
# Convert import pages * into 1 line
# Move functions to utils

@pytest.mark.wip
def test_example(page: Page) -> None:
    page.goto("/")
    BcssLoginPage(page).login_as_user_bcss401()

    # 2 - Create plan
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_planning_and_monitoring_page()
    page.get_by_role("link", name="BCS001").click()
    page.get_by_role("button", name="Create a Plan").click()
    page.get_by_role("link", name="Set all").click()
    page.get_by_placeholder("Enter daily invitation rate").fill("1")
    page.get_by_role("button", name="Update").click()
    page.get_by_role("button", name="Confirm").click()
    page.get_by_role("link", name="Set all").click()
    page.get_by_role("button", name="Close").click()
    page.get_by_role("button", name="Save").click()
    page.get_by_placeholder("Enter note").fill("test data")
    page.locator("#saveNote").get_by_role("button", name="Save").click()

    # Generate Invitations
    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_call_and_recall_page()
    CallAndRecall(page).go_to_generate_invitations_page()
    page.get_by_role("button", name="Generate Invitations").click()

    page.wait_for_selector("#displayRS", timeout=5000)

    # Initially, ensure the table contains "Queued"
    expect(page.locator("#displayRS")).to_contain_text("Queued")

    # Set timeout parameters
    timeout = 120000  # Total timeout of 120 seconds (in milliseconds)
    wait_interval = 10000  # Wait 10 seconds between refreshes (in milliseconds)
    elapsed = 0

    # Loop until the table no longer contains "Queued"
    while elapsed < timeout:
        table_text = page.locator("#displayRS").text_content()
        if "Queued" in table_text or "In Progress" in table_text:
            # Click the Refresh button
            page.get_by_role("button", name="Refresh").click()
            page.wait_for_timeout(wait_interval)
            elapsed += wait_interval
        elif "Failed" in table_text:
            pytest.fail("Invitation has failed to generate")
        else:
            break

    # Final check: ensure that the table now contains "Completed"
    expect(page.locator("#displayRS")).to_contain_text("Completed")

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
    pre_invitation_cells = page.locator(f"//td[text()='{batch_description}']")

    if pre_invitation_cells.count() == 0 and batch_description == "Pre-invitation (FIT) (digital leaflet)":
        print(f"No S1 Pre-invitation (FIT) (digital leaflet) batch found. Skipping to next step")
        return
    elif pre_invitation_cells.count() == 0 and page.locator("td", has_text="No matching records found"):
        pytest.fail(f"No {batch_type} {batch_description} batch found")

    for i in range(pre_invitation_cells.count()):
        row = pre_invitation_cells.nth(i).locator("..")  # Get the parent row

        # Check if the row contains "Prepared" or "Open"
        if row.locator("td", has_text="Prepared").count() > 0 or row.locator("td", has_text="Open").count() > 0:
            # Find the first link in that row and click it
            link = row.locator("a").first
            link_text = link.inner_text()  # Get the batch id dynamically
            link.click()
            break
        else:
            pytest.fail(f"No open/prepared '{batch_type} - {batch_description}' batch found")

    # Checks to see if batch is already prepared
    page.wait_for_timeout(3000) # Without this timeout prepare_button is always set to false
    prepare_button = page.get_by_role("button", name="Prepare Batch").is_visible()

    #If not prepared it will click on the prepare button
    if prepare_button:
        page.get_by_role("button", name="Prepare Batch").click()

    page.locator('text="Retrieve"').nth(0).wait_for()
    page.wait_for_timeout(5000) # This 5 second wait is to allow other Retrieve buttons to show as they do not show up at the same time

    # This loops through each Retrieve button and clicks each one
    for retrieve_button in range (page.get_by_role("button", name="Retrieve").count()):
        # Start waiting for the pdf download
        with page.expect_download() as download_info:
            # Perform the action that initiates download
            page.get_by_role("button", name="Retrieve").nth(retrieve_button-1).click()
        download_file = download_info.value
        file = download_file.suggested_filename
        # Wait for the download process to complete and save the downloaded file in a temp folder
        download_file.save_as(file)
        page.wait_for_timeout(1000)
        if file.endswith(".pdf"):
            nhs_no = pdf_Reader(file)
            os.remove(file) # Deletes the file after extracting the necessary data
        elif file.endswith(".csv"):
            csv_df = csv_Reader(file) # Currently no use in compartment 1, will be necessary for future compartments
            os.remove(file) # Deletes the file after extracting the necessary data

    page.locator('text="Confirm Printed"').nth(0).wait_for()
    page.wait_for_timeout(1000) # This 1 second wait is to allow other Confirm printed buttons to show as they do not show up at the same time

    # This loops through each Confirm printed button and clicks each one
    for _ in range (page.get_by_role("button", name="Confirm Printed").count()):
        page.on("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Confirm Printed").nth(0).click()
        page.wait_for_timeout(1000)

    # Add wait for batch successfully archived

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
                    nhs_no = res = "".join([ele for ele in split_text if ele.isdigit()])
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
