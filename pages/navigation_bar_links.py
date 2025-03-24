from playwright.sync_api import Page
from utils.click_helper import click


class NavigationBar:
    def __init__(self, page: Page):
        self.page = page
        # Navigation Bar - links
        self.back_link = self.page.get_by_role("link", name="Back")
        self.main_menu_link = self.page.get_by_role("link", name="Main Menu")
        self.select_org_link = self.page.get_by_role("link", name="Select Org")
        self.help_link = self.page.get_by_role("link", name="Help")
        self.log_out_link = self.page.get_by_role("link", name="Log-out")

    def click_main_menu_link(self):
        for _ in range(3):  # Try up to 3 times
            if self.main_menu_link.is_visible():
                self.main_menu_link.click()
                return  # Exit if successful

    def click_back_link(self):
        click(self.page, self.back_link)

    def click_select_org_link(self):
        click(self.page, self.click_select_org_link)

    def click_help_link(self):
        click(self.page, self.help_link)

    def click_log_out_link(self):
        click(self.page, self.log_out_link)
