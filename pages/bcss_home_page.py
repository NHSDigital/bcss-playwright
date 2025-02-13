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
        self.contacts_list = self.page.get_by_role("link", name="Contacts List")

    def click_sub_menu_link(self) -> None:
        self.sub_menu_link.click()

    def click_hide_sub_menu_link(self) -> None:
        self.hide_sub_menu_link.click()

    def click_select_org_link(self) -> None:
        self.select_org_link.click()

    def click_back_button(self) -> None:
        self.back_button.click()

    def click_release_notes_link(self) -> None:
        self.release_notes_link.click()

    def click_refresh_alerts_link(self) -> None:
        self.refresh_alerts_link.click()

    def click_user_guide_link(self) -> None:
        self.user_guide_link.click()

    def click_help_link(self) -> None:
        self.help_link.click()

    def click_screening_pracitioners_appointments(self) -> None:
        self.screening_pracitioners_appointments.click()

    def click_contacts_list(self) -> None:
        self.contacts_list.click()

    def click_logout(self) -> None:
        self.log_out.click()
