from playwright.sync_api import Page


class BcssHomePage:

    def __init__(self, page: Page):
        self.page = page

        # Top menu bar
        self.sub_menu_link = self.page.get_by_role("link", name="Show Sub-menu")
        self.hide_sub_menu_link = self.page.get_by_role("link", name="Hide Sub-menu")
        self.back_button = self.page.get_by_role("link", name="Back")
        self.main_menu = self.page.get_by_role("link", name="Main Menu")
        self.select_org_link = self.page.get_by_role("link", name="Select Org")
        self.help_link = self.page.get_by_role("link", name="Help")
        self.log_out = self.page.get_by_role("link", name="Log-out")

        # Alerts
        self.refresh_alerts_link = self.page.get_by_role("link", name="Refresh alerts")

        # Footer
        self.release_notes_link = self.page.get_by_role("link", name="- Release Notes")
        self.user_guide_link = self.page.get_by_role("link", name="User guide")

        # Main Menu
        self.screening_pracitioners_appointments = self.page.get_by_role(
            "link", name="Screening Practitioner Appointments"
        )

    def click_sub_menu_link(self):
        self.sub_menu_link.click()

    def click_hide_sub_menu_link(self):
        self.hide_sub_menu_link.click()

    def click_select_org_link(self):
        self.select_org_link.click()

    def click_back_button(self):
        self.back_button.click()

    def click_release_notes_link(self):
        self.release_notes_link.click()

    def click_refresh_alerts_link(self):
        self.refresh_alerts_link.click()

    def click_user_guide_link(self):
        self.user_guide_link.click()

    def click_help_link(self):
        self.help_link.click()

    def click_screening_pracitioners_appointments(self):
        self.screening_pracitioners_appointments.click()
