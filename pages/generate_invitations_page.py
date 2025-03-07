from playwright.sync_api import Page, expect
import pytest


class GenerateInvitations:
    def __init__(self, page: Page):
        self.page = page
        # Generate Invitations - page links
        self.generate_invitations_button = self.page.get_by_role("button", name="Generate Invitations")
        self.displayRS = self.page.locator("#displayRS")
        self.refresh_button = self.page.get_by_role("button", name="Refresh")
        self.planned_invitations_total = self.page.locator("#col8_total")

    def click_generate_invitations_button(self):
        self.generate_invitations_button.click()

    def click_refresh_button(self):
        self.refresh_button.click()

    def wait_for_invitation_generation_complete(self):
        self.page.wait_for_selector("#displayRS", timeout=5000)

        if self.planned_invitations_total == "0":
            pytest.fail("There are no planned invitations to generate")

        # Initially, ensure the table contains "Queued"
        expect(self.displayRS).to_contain_text("Queued")

        # Set timeout parameters
        timeout = 120000  # Total timeout of 120 seconds (in milliseconds)
        wait_interval = 5000  # Wait 5 seconds between refreshes (in milliseconds)
        elapsed = 0

        # Loop until the table no longer contains "Queued"
        while elapsed < timeout:
            table_text = self.displayRS.text_content()
            if "Queued" in table_text or "In Progress" in table_text:
                # Click the Refresh button
                self.click_refresh_button()
                self.page.wait_for_timeout(wait_interval)
                elapsed += wait_interval
            elif "Failed" in table_text:
                pytest.fail("Invitation has failed to generate")
            else:
                break

        # Final check: ensure that the table now contains "Completed"
        expect(self.displayRS).to_contain_text("Completed")

        value = self.planned_invitations_total.text_content().strip()  # Get text and remove extra spaces
        if int(value) <= 5:
            pytest.fail("There are less than 5 invitations generated")
