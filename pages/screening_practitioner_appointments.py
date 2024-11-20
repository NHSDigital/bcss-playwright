from playwright.sync_api import Page


class ScreeningPractitionerAppointments:

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
        self.view_appointments = self.page.get_by_role("link", name="View appointments")
        self.patients_that_require_colonoscopy_assessment_appointments = (
            self.page.get_by_role(
                "link", name="Patients that Require Colonoscopy Assessment Appointments"
            )
        )
        self.patients_that_require_colonoscopy_assessment_appointments_bowl_scope = (
            self.page.get_by_role(
                "link",
                name="Bowel Scope",
            )
        )
        self.patients_that_require_surveillance_appointments = self.page.get_by_role(
            "link", name="Patients that Require Surveillance Appointments"
        )
        self.patients_that_require_post_investigation_appointments = (
            self.page.get_by_role(
                "link", name="Patients that Require Post-Investigation Appointments"
            )
        )
        self.set_availability = self.page.get_by_role("link", name="Set Availability")

    # Top menu interactions
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

    # Main Menu interactions
    def click_view_appointments(self):
        self.view_appointments.click()

    def click_patients_that_require_colonoscopy_assessment_appointments(self):
        self.patients_that_require_colonoscopy_assessment_appointments.click()

    def click_patients_that_require_colonoscopy_assessment_appointments_bowl_scope(
        self,
    ):
        self.patients_that_require_colonoscopy_assessment_appointments_bowl_scope.click()

    def click_patients_that_require_surveillance_appointments(self):
        self.patients_that_require_surveillance_appointments.click()

    def click_patients_that_require_post_investigation_appointments(self):
        self.patients_that_require_post_investigation_appointments.click()

    def click_set_availability(self):
        self.set_availability.click()
