from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from typing import Dict

class SpineSearchPage:
    """
    Page object for the Spine Search screen, enabling demographic searches
    and data retrieval from the Spine system.
    """
    def __init__(self, page: Page):
        self.page = page
        self.spine_url = "https://bcss-bcss-18680-ddc-bcss.k8s-nonprod.texasplatform.uk/servlet/SpineSearchScreen"

        # Define locators
        self.retrieve_data_link = self.page.get_by_role("link", name="Retrieve Data from Spine")
        self.demographics_radio = self.page.get_by_role("radio", name="Demographics")
        self.date_of_birth_field = self.page.locator("#dateOfBirth")

        # Represents the calendar cell for the 6th day in the date picker
        self.date = self.page.get_by_role("cell", name="6").first

        self.surname_field = self.page.locator("#surname")
        self.forename_field = self.page.locator("#forename")
        self.gender_dropdown = self.page.locator("#gender")
        self.postcode_field = self.page.locator("#postcode")
        self.search_button = self.page.get_by_role("button", name="Search")
        self.alert_message = self.page.get_by_role("alert")

    def navigate_to_spine_search(self):
        self.retrieve_data_link.click()
        self.page.goto(self.spine_url)

    def select_demographic_search(self):
        self.demographics_radio.check()

    def enter_search_criteria(self, dob: str, surname: str, forename: str, gender: str, postcode: str):
        self.date_of_birth_field.click()
        self.date.click()
        self.surname_field.fill(surname)
        self.forename_field.fill(forename)
        gender_option = {"Male": "1", "Female": "2"}.get(gender, "1")
        self.gender_dropdown.select_option(gender_option)
        self.postcode_field.fill(postcode)

    def perform_search(self):
        self.search_button.click()

    def get_spine_alert_message(self) -> str:
        return self.alert_message.inner_text() if self.alert_message.is_visible() else ""
