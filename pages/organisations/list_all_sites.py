import logging
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from enum import StrEnum
from utils.table_util import TableUtils


class ListAllSites(BasePage):
    """List All Sites Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Initialize TableUtils for the table with id="displayRS"
        self.list_all_org_table = TableUtils(page, "#listAllOrgsTable")

        # List All Organisations links
        self.select_site_type = self.page.locator("#siteTypeId")
        self.create_new_site = self.page.get_by_role("button", name="Create New Site")

    def select_site_type_option(self, option: str) -> None:
        """
        This method is designed to select a specific site type from the List All Sites page.
        """
        self.select_site_type.select_option(option)

    def click_create_new_site(self) -> None:
        """Clicks the 'Create New Org' button."""
        self.create_new_site.click()


class SiteType(StrEnum):
    CARE_TRUST_SITE = "1020"
    NHS_TRUST_SITE = "1018"
    PCT_SITE = "1019"
    PATHOLOGY_LABORATORY_SITE = "306448"
