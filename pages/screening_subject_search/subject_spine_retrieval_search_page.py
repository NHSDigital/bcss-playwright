from playwright.sync_api import Page, expect
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

    def navigate_to_spine_search(self):
        """
        Navigates to the Spine Search screen by clicking the appropriate link and
        loading the target URL.
        """
        self.page.get_by_role("link", name="Retrieve Data from Spine").click()
        self.page.goto(self.spine_url)

    def select_demographic_search(self):
        """
        Selects the 'Demographics' radio button to enable demographic-based search.
        """
        self.page.get_by_role("radio", name="Demographics").check()

    def enter_search_criteria(self, dob: str, surname: str, forename: str, gender: str, postcode: str):
        """Fills in demographic search fields with user details."""
        # Date of Birth
        self.page.locator("#dateOfBirth").click()
        self.page.get_by_role("cell", name="6").first.click()

        # Surname
        self.page.locator("#surname").fill(surname)

        # Forename
        self.page.locator("#forename").fill(forename)

        # Gender
        gender_option = {"Male": "1", "Female": "2"}.get(gender, "1")
        self.page.locator("#gender").select_option(gender_option)

        # Postcode
        self.page.locator("#postcode").fill(postcode)

    def perform_search(self):
        """
        Clicks the 'Search' button to initiate the demographic search.
        """
        self.page.get_by_role("button", name="Search").click()


    def get_spine_alert_message(self) -> str:
        """
        Retrieve the visible alert message from the page, if any.

        Returns:
            str: The inner text of the alert element if it's visible;
            otherwise, an empty string.
        """
        self.alert_message = self.page.get_by_role("alert")
        if self.alert_message.is_visible():
            return self.alert_message.inner_text()
        else:
            return ""

