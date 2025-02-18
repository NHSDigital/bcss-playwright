import re
import pytest
from playwright.sync_api import Page, expect


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
    page.get_by_role("link", name="BCS009").click()
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
    page.get_by_role("link", name="Main Menu").click()
    page.get_by_role("link", name="Call and Recall").click()
    page.get_by_role("link", name="Generate Invitations").click()
    page.get_by_role("button", name="Generate Invitations").click()
    # #TODO Add loop for below steps
    # expect(page.locator("#displayRS")).to_contain_text("Queued")
    # page.get_by_role("button", name="Refresh").click()
    # expect(page.locator("#displayRS")).to_contain_text("Completed")

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
        else:
            break

    # Final check: ensure that the table now contains "Completed"
    expect(page.locator("#displayRS")).to_contain_text("Completed")

    # Print the batch of Pre-Invitation Letters
    page.get_by_role("link", name="Main Menu").click()
    page.get_by_role("link", name="Communications Production").click()
    page.get_by_role("link", name="Active Batch List").click()
    page.locator("#eventCodeFilter").click()
    page.locator("#eventCodeFilter").fill("S1")
    page.locator("#eventCodeFilter").press("Enter")
    pre_invitation_cells = page.locator("//td[text()='Pre-invitation (FIT)']")

    for i in range(pre_invitation_cells.count()):
        row = pre_invitation_cells.nth(i).locator("..")  # Get the parent row

        # Check if the row contains "Prepared" or "Open"
        if row.locator("td", has_text="Prepared").count() > 0 or row.locator("td", has_text="Open").count() > 0:
            # Find the first link in that row and click it
            link = row.locator("a").first
            link_text = link.inner_text()  # Get the link text dynamically
            link.click()
    page.get_by_text("Open In-Queue Processing Prepared Type : Original Priority : High Deadline : 17").click()


from pypdf import PdfReader

@pytest.mark.wip2
def test_example(page: Page) -> None:
    page.goto("/")
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill("BCSS401")
    page.get_by_role("textbox", name="Username").press("Tab")
    page.get_by_role("textbox", name="Password").fill("changeme")
    page.get_by_role("button", name="submit").click()

     # Print the batch of Pre-Invitation Letters
    page.get_by_role("link", name="Communications Production").click()
    page.get_by_role("link", name="Active Batch List").click()
    page.locator("#eventCodeFilter").click()
    page.locator("#eventCodeFilter").fill("S1")
    page.locator("#eventCodeFilter").press("Enter")
    pre_invitation_cells = page.locator("//td[text()='Pre-invitation (FIT)']")

    for i in range(pre_invitation_cells.count()):
        row = pre_invitation_cells.nth(i).locator("..")  # Get the parent row

        # Check if the row contains "Prepared" or "Open"
        if row.locator("td", has_text="Prepared").count() > 0 or row.locator("td", has_text="Open").count() > 0:
            break
            # # Find the first link in that row and click it
            # link = row.locator("a").first
            # link_text = link.inner_text()  # Get the link text dynamically
            # link.click()
        else:
            page.get_by_role("button", name="Prepare Batch").click()
            page.wait_for_timeout(10000)

        # Start waiting for the download
        with page.expect_download() as download_info:
            # Perform the action that initiates download
            page.get_by_role("button", name="Retrieve").click()
        download = download_info.value

        # Wait for the download process to complete and save the downloaded file somewhere
        download.save_as(f"/temp/{download.suggested_filename}")


        reader = PdfReader(f"/temp/{download.suggested_filename}")
        #For loop looping through all pages of the file to find the NHS Number
        for pages in reader.pages:
            text = pages.extract_text()
            if "NHS No" in text:
                #If NHS number is found split the text by every new line into a list
                text = text.splitlines(True)
                for split_text in text:
                    if "NHS No" in split_text:
                        #If a string is found containing "NHS No" all characters but digits are stored into nhs_no
                        nhs_no = res = "".join([ele for ele in split_text if ele.isdigit()])
                        break
                    # print(nhs_no) 9849028742
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Confirm Printed").click()
    expect(page.get_by_text("Batch Successfully Archived")).to_be_visible()
    page.get_by_role("link", name="Back").click()
    page.get_by_role("link", name="Archived Batch List").click()
    page.get_by_role("cell", name="Date Archived : Activate to").locator("span").nth(1).click()
    page.get_by_role("cell", name="Date Archived : Activate to").click()
    # Change below to check if first row is  the same as the batch we just archived
    # expect(page.get_by_role("cell", name="S1").first).to_be_visible()
    # expect(page.get_by_role("cell", name="Pre-invitation (FIT)").first).to_be_visible()
    # expect(page.get_by_role("link", name="8848")).to_be_visible()
    page.get_by_role("link", name="Main Menu").click()
    page.get_by_role("link", name="Screening Subject Search").click()
    page.get_by_role("textbox", name="NHS Number").click()
    page.get_by_role("textbox", name="NHS Number").fill(nhs_no)
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_role("cell", name="Subject Screening Summary", exact=True)).to_be_visible()
    page.get_by_role("link", name="Main Menu").click()
    page.get_by_role("link", name="Communications Production").click()
    page.get_by_role("link", name="Active Batch List").click()
