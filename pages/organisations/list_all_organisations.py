from playwright.sync_api import Page
from pages.base_page import BasePage
from enum import StrEnum

class ListAllOrganisations(BasePage):
    """Organisations And Site Details Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # List All Organisations links
        self.select_organisation_type = self.page.locator("#organisationType")

    def select_organisation_type_option(self, option: str) -> None:  
        """
        This method is designed to select a specific organisation type from the List All Organisations page.
        Args:
            option (str): The organisation type option to be selected. This should be a string that matches one of the available options in the dropdown menu.
        Returns:
            None
        """
        self.select_organisation_type.select_option(option)  


class OrganisationType(StrEnum):
    BCS_PROGRAMME_HUB = "1002"
    BCS_QA_TEAM = "202189"
    BCS_SCREENING_CENTRE = "1003"
    BCSS_SERVICE_MANAGER = "1036"
    CCG = "1006"
    CARE_TRUST = "1007"
    GP_PRACTICE = "1009"
    ICB= "1004"
    IT_CLUSTER="1001"
    NHS_BOWEL_CANCER_SCREENING_PROGRAMME = "1000"
    NHS_TRUST = "1005"
    PUBLIC_HEALTH_ENGLAND= "202130"
