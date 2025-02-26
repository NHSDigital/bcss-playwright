import pytest
from pypdf import PdfReader
from playwright.sync_api import Page, expect
import pandas as pd
import sys
sys.path.append("../utils")
from utils.oracle import *

@pytest.mark.wip
def test_example(page: Page) -> None:
    page.goto("/")
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill("BCSS401")
    page.get_by_role("textbox", name="Username").press("Tab")
    page.get_by_role("textbox", name="Password").fill("changeme")
    page.get_by_role("button", name="submit").click()

    # Create plan
    page.get_by_role("link", name="Call and Recall").click()
    page.get_by_role("link", name="Planning and Monitoring").click()
    page.get_by_role("link", name="BCS001").click()
    page.get_by_role("button", name="Create a Plan").click()
    page.get_by_role("link", name="Set all").click()
    page.get_by_placeholder("Enter weekly invitation rate").fill("1")
    page.get_by_role("button", name="Update").click()
    page.get_by_role("button", name="Confirm").click()
    page.get_by_role("link", name="Set all").click()
    page.get_by_role("button", name="Close").click()
    page.get_by_role("button", name="Save").click()
    page.get_by_placeholder("Enter note").fill("test data")
    page.locator("#saveNote").get_by_role("button", name="Save").click()

    # Generate Invitations
    main_menu_available(page)
    page.get_by_role("link", name="Call and Recall").click()
    page.get_by_role("link", name="Generate Invitations").click()
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
        if "Queued" in table_text:
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
    batch_processing(page, "S1", "Pre-invitation (FIT) (digital leaflet)", "S9 - Pre-invitation Sent") # Sometimes it is "S10 - Invitation & Test Kit Sent"

    database_connection_exec("bcss_timed_events")

    # Print the batch of Invitation & Test Kit Letters
    batch_processing(page, "S9", "Invitation & Test Kit (FIT)", "S10 - Invitation & Test Kit Sent")

    # Print a set of reminder letters
    batch_processing(page, "S10", "Test Kit Reminder", "S19 - Reminder of Initial Test Sent")

    # Log out
    page.get_by_role("link", name="Log-out").click()
    expect(page.get_by_role("heading", name="You have logged out")).to_be_visible()

def batch_processing(page: Page, batch_type: str, batch_description: str, latest_event_status: str):
    main_menu_available(page)
    page.get_by_role("link", name="Communications Production").click()
    page.get_by_role("link", name="Active Batch List").click()
    page.locator("#eventCodeFilter").click()
    page.locator("#eventCodeFilter").fill(batch_type)
    page.locator("#eventCodeFilter").press("Enter")
    pre_invitation_cells = page.locator(f"//td[text()='{batch_description}']")

    for i in range(pre_invitation_cells.count()):
        row = pre_invitation_cells.nth(i).locator("..")  # Get the parent row

        # Check if the row contains "Prepared" or "Open"
        if row.locator("td", has_text="Prepared").count() > 0 or row.locator("td", has_text="Open").count() > 0 or row.locator("td", has_text="Closed").count() > 0:
            # Find the first link in that row and click it
            link = row.locator("a").first
            link_text = link.inner_text()  # Get the link text dynamically
            link.click()
        else:
            pytest.fail(f"No {batch_type} batch found")

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
        download_file.save_as(f"/temp/{file}")
        page.wait_for_timeout(1000)
        if file.endswith(".pdf"):
            nhs_no = pdf_Reader(file)
        elif file.endswith(".csv"):
            csv_df = csv_Reader(file)

    page.locator('text="Confirm Printed"').nth(0).wait_for()
    page.wait_for_timeout(1000) # This 1 second wait is to allow other Confirm printed buttons to show as they do not show up at the same time

    # This loops through each Confirm printed button and clicks each one
    for confirm_button in range (page.get_by_role("button", name="Confirm Printed").count()):
        page.on("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Confirm Printed").nth(0).click()
        page.wait_for_timeout(1000)

    main_menu_available(page)
    page.get_by_role("link", name="Communications Production").click()
    page.get_by_role("link", name="Archived Batch List").click()
    page.locator("#batchIdFilter").click()
    page.locator("#batchIdFilter").fill(link_text)
    page.locator("#batchIdFilter").press("Enter")
    expect(page.locator("td").filter(has_text=link_text)).to_be_visible() # Checks to see if the batch is now archived

    subject_search_by_nhs_no(page, nhs_no, latest_event_status)

def pdf_Reader(file: str):
    reader = PdfReader(f"/temp/{file}")

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
    csv_df = pd.read_csv(f"/temp/{file}")
    return csv_df

def subject_search_by_nhs_no(page: Page, nhs_no: str, latest_event_status: str):
    main_menu_available(page)
    page.get_by_role("link", name="Screening Subject Search").click()
    page.get_by_role("textbox", name="NHS Number").click()
    page.get_by_role("textbox", name="NHS Number").fill(nhs_no)
    page.get_by_role("textbox", name="NHS Number").press("Enter")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_role("cell", name="Subject Screening Summary", exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name="Latest Event Status", exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name=latest_event_status, exact=True)).to_be_visible()

def main_menu_available(page: str):
    is_main_menu_available = page.get_by_role("link", name="Main Menu").is_visible()

    if is_main_menu_available:
        page.get_by_role("link", name="Main Menu").click()
