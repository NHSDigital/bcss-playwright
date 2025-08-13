from datetime import datetime
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from typing import Dict

# Assume you have a CalendarPicker utility in your project
from utils.calendar_picker import CalendarPicker

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
        self.surname_field = self.page.locator("#surname")
        self.forename_field = self.page.locator("#forename")
        self.gender_dropdown = self.page.locator("#gender")
        self.postcode_field = self.page.locator("#postcode")
        self.search_button = self.page.get_by_role("button", name="Search")
        self.alert_message = self.page.locator(".spine-alert")

        # CalendarPicker utility instance
        self.calendar_picker = CalendarPicker(self.page)

    def navigate_to_spine_search(self) -> None:
        """
        Navigates to the Spine Search screen by clicking the appropriate link
        and loading the target URL.
        """
        self.retrieve_data_link.click()
        self.page.goto(self.spine_url)

    def select_demographic_search(self) -> None:
        """
        Selects the 'Demographics' radio button to enable demographic search mode.
        """
        self.demographics_radio.check()

    def enter_search_criteria(
    self, dob: str, surname: str, forename: str, gender: str, postcode: str
) -> None:
        """
        Fills in the demographic search fields with the provided values.

        Args:
        dob (str): Date of birth in string format (e.g., "06 May 1940").
        surname (str): Subject's surname.
        forename (str): Subject's forename.
        gender (str): Gender value ("Male" or "Female").
        postcode (str): Subject's postcode.
        """

        # Convert dob string to datetime object
        dob_dt = datetime.strptime(dob, "%d %b %Y")  # Adjust format if needed
        self.date_of_birth_field.click()
        self.calendar_picker.v2_calendar_picker(dob_dt)  # dob should be in a supported format, e.g. "YYYY-MM-DD"
        self.surname_field.fill(surname)
        self.forename_field.fill(forename)
        gender_option = {"Male": "1", "Female": "2"}.get(gender, "1")
        self.gender_dropdown.select_option(gender_option)
        self.postcode_field.fill(postcode)

    def perform_search(self) -> None:
        """
        Clicks the 'Search' button to initiate the Spine demographic search.
        """
        self.search_button.click()

    def get_spine_alert_message(self) -> str:
        alert_locator = self.page.locator(".spine-alert")  # Update selector if needed
        try:
            alert_locator.wait_for(state="visible", timeout=5000)
            return alert_locator.inner_text().strip()
        except TimeoutError:
            print("Alert message not visible within timeout.")
            return ""
        except Exception as e:
            print(f"Unexpected error while fetching alert: {e}")
            return ""
