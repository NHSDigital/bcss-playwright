import logging
from playwright.sync_api import Page
from pages.base_page import BasePage


class ViewContactsPage(BasePage):
    """View Contacts Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # View Contacts - page locators, methods

    def verify_view_contacts_title(self) -> None:
        """Verify the View Contacts page title is displayed correctly"""
        self.bowel_cancer_screening_page_title_contains_text("View Contacts")

    def search_by_job_role_and_organisation_code(
        self, job_role: str, org_code: str
    ) -> None:
        """
        search by provided job role and organisation
        """
        self.page.locator('input[name="selJobRole"]').fill(job_role)
        self.page.locator('input[name="selOrganisationCode"]').fill(org_code)
        self.page.get_by_role("button", name="Search").click()
        logging.info(f"input {job_role} and {org_code} and click on search")
