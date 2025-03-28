from playwright.sync_api import Page, expect
import pytest
from utils.click_helper import click
import logging

class GenerateInvitations:
    def __init__(self, page: Page):
        self.page = page
        # Generate Invitations - page links
        self.generate_invitations_button = self.page.get_by_role("button", name="Generate Invitations")
        self.displayRS = self.page.locator("#displayRS")
        self.refresh_button = self.page.get_by_role("button", name="Refresh")
        self.planned_invitations_total = self.page.locator("#col8_total")
        self.self_referrals_total = self.page.locator("#col9_total")

    def click_generate_invitations_button(self):
        click(self.page, self.generate_invitations_button)

    def click_refresh_button(self):
        click(self.page, self.refresh_button)

    def wait_for_invitation_generation_complete(self) -> bool:
        """
        This function is used to wait for the invitations to be generated.
        Every 5 seconds it refreshes the table and checks to see if the invitations have been generated.
        It also checks that enough invitations were generated and checks to see if self referrals are present
        """
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
        logging.info(f"Waiting for successful generation")
        while elapsed < timeout: # there may be a stored procedure to speed this process up
            table_text = self.displayRS.text_content()
            if "Failed" in table_text:
                pytest.fail("Invitation has failed to generate")
            elif "Queued" in table_text or "In Progress" in table_text:
                # Click the Refresh button
                self.click_refresh_button()
                self.page.wait_for_timeout(wait_interval)
                elapsed += wait_interval
            else:
                break

        # Final check: ensure that the table now contains "Completed"
        try:
            expect(self.displayRS).to_contain_text("Completed")
            logging.info("Invitations successfully generated")
            logging.info(f"Invitations took {elapsed/1000} seconds to generate")
        except Exception as e:
            pytest.fail("Invitations not generated successfully")

        value = self.planned_invitations_total.text_content().strip()  # Get text and remove extra spaces
        if int(value) < 5:
            pytest.fail("There are less than 5 invitations generated")

        self_referrals_total = int(self.self_referrals_total.text_content().strip())
        if self_referrals_total >= 1:
            return True
        else:
            logging.warning("No S1 Digital Leaflet batch will be generated")
            return False
