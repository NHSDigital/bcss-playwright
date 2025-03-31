from playwright.sync_api import Page
from utils.click_helper import click

class SubjectScreeningPage:
    def __init__(self, page: Page):
        self.page = page
        # Subject Search Criteria - page filters
        self.episodes_filter = self.page.get_by_role("radio", name="Episodes")
        self.demographics_filter = self.page.get_by_role("radio", name="Demographics")
        self.datasets_filter = self.page.get_by_role("radio", name="Datasets")
        self.nhs_number_filter = self.page.get_by_role("textbox", name="NHS Number")
        self.surname_filter = self.page.locator("#A_C_Surname")
        self.soundex_filter = self.page.get_by_role("checkbox", name="Use soundex")
        self.forename_filter = self.page.get_by_role("textbox", name="Forename")
        self.date_of_birth_filter = self.page.locator("#A_C_DOB_From")
        self.data_of_birth_range_filter = self.page.get_by_role("textbox", name="(for a date range, enter a to")
        self.postcode_filter = self.page.get_by_role("textbox", name="Postcode")
        self.episode_closed_date_filter = self.page.get_by_role("textbox", name="Episode Closed Date")
        self.kit_batch_number_filter = self.page.get_by_role("textbox", name="Kit Batch Number")
        self.kit_number_filter = self.page.get_by_role("textbox", name="Kit Number")
        self.fit_device_id_filter = self.page.get_by_role("textbox", name="FIT Device ID")
        self.laboratory_name_filter = self.page.get_by_role("textbox", name="Laboratory Name")
        self.laboratory_test_date_filter = self.page.get_by_role("textbox", name="Laboratory Test Date")
        self.diagnostic_test_actual_date_filter = self.page.get_by_role("textbox", name="Diagnostic Test Actual Date")
        self.search_button = self.page.get_by_role("button", name="Search")
        self.search_area = self.page.locator("#A_C_SEARCH_DOMAIN")

    def select_whole_database_search_area(self):
        self.search_area.select_option("07")

    def click_search_button(self):
        click(self.page, self.search_button)

    def click_episodes_filter(self):
        self.episodes_filter.check()

    def click_demographics_filter(self):
        self.demographics_filter.check()

    def click_datasets_filter(self):
        self.datasets_filter.check()

    def click_nhs_number_filter(self):
        click(self.page, self.nhs_number_filter)

    def click_surname_filter(self):
        click(self.page, self.surname_filter)

    def click_soundex_filter(self):
        self.soundex_filter.check()

    def click_forename_filter(self):
        click(self.page, self.forename_filter)

    def click_date_of_birth_filter(self):
        click(self.page, self.date_of_birth_filter)

    def click_date_of_birth_range_filter(self):
        click(self.page, self.data_of_birth_range_filter)

    def click_postcode_filter(self):
        click(self.page, self.postcode_filter)

    def click_episodes_closed_date_filter(self):
        click(self.page, self.episode_closed_date_filter)

    def click_kit_batch_number_filter(self):
        click(self.page, self.kit_batch_number_filter)

    def click_kit_number_filter(self):
        click(self.page, self.kit_number_filter)

    def click_fit_device_id_filter(self):
        click(self.page, self.fit_device_id_filter)

    def click_laboratory_name_filter(self):
        click(self.page, self.laboratory_name_filter)

    def click_laboratory_test_date_filter(self):
        click(self.page, self.laboratory_test_date_filter)

    def click_diagnostic_test_actual_date_filter(self):
        click(self.page, self.diagnostic_test_actual_date_filter)
