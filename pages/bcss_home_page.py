from playwright.sync_api import Page, expect
from utils.click_helper import click


class BcssHomePage:
    def __init__(self, page: Page):
        self.page = page
        # Homepage links
        self.sub_menu_link = self.page.get_by_role("link", name="Show Sub-menu")
        self.hide_sub_menu_link = self.page.get_by_role("link", name="Hide Sub-menu")
        self.select_org_link = self.page.get_by_role("link", name="Select Org")
        self.back_button = self.page.get_by_role("link", name="Back")
        self.release_notes_link = self.page.get_by_role("link", name="- Release Notes")
        self.refresh_alerts_link = self.page.get_by_role("link", name="Refresh alerts")
        self.user_guide_link = self.page.get_by_role("link", name="User guide")
        self.help_link = self.page.get_by_role("link", name="Help")
        # Bowel Cancer Screening System header
        self.bowel_cancer_screening_system_header = self.page.locator("#ntshAppTitle")

    def click_sub_menu_link(self)->None:
        click(self.page, self.sub_menu_link)

    def click_hide_sub_menu_link(self)->None:
        click(self.page, self.hide_sub_menu_link)

    def click_select_org_link(self)->None:
        click(self.page, self.select_org_link)

    def click_back_button(self)->None:
        click(self.page, self.back_button)

    def click_release_notes_link(self)->None:
        click(self.page, self.release_notes_link)

    def click_refresh_alerts_link(self)->None:
        click(self.page, self.refresh_alerts_link)

    def click_user_guide_link(self)->None:
        click(self.page, self.user_guide_link)

    def click_help_link(self)->None:
        click(self.page, self.help_link)

    def bowel_cancer_screening_system_header_is_displayed(self)->None:
        expect(self.bowel_cancer_screening_system_header).to_contain_text("Bowel Cancer Screening System")


class MainMenu:
    def __init__(self, page: Page):
        self.page = page
        # Main menu - page links
        self.contacts_list_page = self.page.get_by_role("link", name="Contacts List")
        self.bowel_scope_page = self.page.get_by_role("link", name="Bowel Scope")
        self.call_and_recall_page = self.page.get_by_role("link", name="Call and Recall")
        self.communications_production_page = self.page.get_by_role("link", name="Communications Production")
        self.download_page = self.page.get_by_role("link", name="Download")
        self.fit_test_kits_page = self.page.get_by_role("link", name="FIT Test Kits")
        self.gfob_test_kits_page = self.page.get_by_role("link", name="gFOBT Test Kits")
        self.lynch_surveillance_page = self.page.get_by_role("link", name="Lynch Surveillance")
        self.organisations_page = self.page.get_by_role("link", name="Organisations")
        self.reports_page = self.page.get_by_role("link", name="Reports")
        self.screening_practitioner_appointments_page = self.page.get_by_role("link", name="Screening Practitioner")
        self.screening_subject_search_page = self.page.get_by_role("link", name="Screening Subject Search")

    def go_to_contacts_list_page(self)->None:
        click(self.page, self.contacts_list_page)

    def go_to_bowel_scope_page(self)->None:
        click(self.page, self.bowel_scope_page)

    def go_to_call_and_recall_page(self)->None:
        click(self.page, self.call_and_recall_page)

    def go_to_communications_production_page(self)->None:
        click(self.page, self.communications_production_page)

    def go_to_download_page(self)->None:
        click(self.page, self.download_page)

    def go_to_fit_test_kits_page(self)->None:
        click(self.page, self.fit_test_kits_page)

    def go_to_gfob_test_kits_page(self)->None:
        click(self.page, self.gfob_test_kits_page)

    def go_to_lynch_surveillance_page(self)->None:
        click(self.page, self.lynch_surveillance_page)

    def go_to_organisations_page(self)->None:
        click(self.page, self.organisations_page)

    def go_to_reports_page(self)->None:
        click(self.page, self.reports_page)

    def go_to_screening_practitioner_appointments_page(self)->None:
        click(self.page, self.screening_practitioner_appointments_page)

    def go_to_screening_subject_search_page(self)->None:
        click(self.page, self.screening_subject_search_page)
