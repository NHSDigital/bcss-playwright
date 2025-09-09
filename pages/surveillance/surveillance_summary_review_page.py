from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class SurveillanceSummaryPage(BasePage):
    """Page object for navigating to and interacting with the Surveillance Review Summary section."""
    def __init__(
        self,
        page,
        org_and_site_details_link_text,
        list_all_orgs_link_text,
        list_all_sites_link_text,
        surveillance_link_text,
        manage_surveillance_review_link_text,
        surveillance_review_summary_header_text,
        back_link_text="Back"
    ):
        self.page = page
        self.org_and_site_details_link = self.page.get_by_role("link", name=org_and_site_details_link_text)
        self.list_all_orgs_link = self.page.get_by_role("link", name=list_all_orgs_link_text)
        self.list_all_sites_link = self.page.get_by_role("link", name=list_all_sites_link_text)
        self.surveillance_link = self.page.get_by_role("link", name=surveillance_link_text, exact=True)
        self.manage_surveillance_review_link = self.page.get_by_role("link", name=manage_surveillance_review_link_text)
        self.surveillance_review_summary_header = self.page.get_by_text(surveillance_review_summary_header_text)
        self.back_link = self.page.get_by_role("link", name=back_link_text, exact=True)

    def navigate_to_surveillance_review_summary(self):
        """Navigates through multiple UI steps to reach the Surveillance Review Summary section."""
        self.org_and_site_details_link.click()
        self.list_all_orgs_link.click()
        self.back_button = self.page.get_by_role("link", name="Back", exact=True)
        self.back_button.click()
        self.list_all_sites_link.click()
        for _ in range(3):
            self.back_button.click()
        self.surveillance_link.click()
        self.manage_surveillance_review_link.click()
