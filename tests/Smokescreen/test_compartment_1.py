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
    #TODO Add loop for below steps
    expect(page.locator("#displayRS")).to_contain_text("Queued")
    page.get_by_role("button", name="Refresh").click()
    expect(page.locator("#displayRS")).to_contain_text("Completed")
