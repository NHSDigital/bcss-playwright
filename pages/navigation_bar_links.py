from playwright.sync_api import Page

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
        self.main_menu_link.click()

    def click_back_link(self):
        self.back_link.click()

    def click_select_org_link(self):
        self.select_org_link.click()

    def click_help_link(self):
        self.help_link.click()

    def click_log_out_link(self):
        self.log_out_link.click()
