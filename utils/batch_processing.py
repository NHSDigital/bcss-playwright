from pages.navigation_bar_links import NavigationBar
from pages.bcss_home_page import MainMenu
from pages.communications_production_page import CommunicationsProduction
from pages.active_batch_list_page import ActiveBatchList
from pages.manage_active_batch_page import ManageActiveBatch
from pages.archived_batch_list_page import ArchivedBatchList
from utils.pdf_reader import extract_nhs_no_from_pdf
from utils.screening_subject_page_searcher import verify_subject_event_status_by_nhs_no
import os
import pytest
from playwright.sync_api import Page

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
            nhs_numbers = extract_nhs_no_from_pdf(file)
            first_nhs_no = nhs_numbers[0]
            os.remove(file) # Deletes the file after extracting the necessary data
        elif file.endswith(".csv"):
            os.remove(file) # Deletes the file after extracting the necessary data

    # This loops through each Confirm printed button and clicks each one
    for _ in range (retrieve_button_count):
        page.on("dialog", lambda dialog: dialog.accept())
        ManageActiveBatch(page).confirm_button.nth(0).click()

    ActiveBatchList(page).batch_successfully_archived_msg.wait_for()

    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_communications_production_page()
    CommunicationsProduction(page).go_to_archived_batch_list_page()
    ArchivedBatchList(page).enter_id_filter(link_text)
    ArchivedBatchList(page).verify_table_data(link_text)

    verify_subject_event_status_by_nhs_no(page, first_nhs_no, latest_event_status)
    return nhs_numbers
