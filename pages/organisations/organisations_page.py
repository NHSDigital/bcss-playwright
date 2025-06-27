from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class OrganisationsPage(BasePage):
    """Organisations Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Organisations page links
        self.screening_centre_parameters_page = self.page.get_by_role(
            "link", name="Screening Centre Parameters"
        )
        self.organisation_parameters_page = self.page.get_by_role(
            "link", name="Organisation Parameters"
        )
        self.organisations_and_site_details_page = self.page.get_by_role(
            "link", name="Organisation and Site Details"
        )
        self.gp_practice_endorsement_page = self.page.get_by_role(
            "link", name="GP Practice Endorsement"
        )
        self.upload_nacs_data_bureau_page = self.page.get_by_role(
            "link", name="Upload NACS data (Bureau)"
        )
        self.bureau_page = self.page.get_by_role("link", name="Bureau")

    def go_to_screening_centre_parameters_page(self) -> None:
        """Clicks the 'Screening Centre Parameters' link."""
        self.click(self.screening_centre_parameters_page)

    def go_to_organisation_parameters_page(self) -> None:
        """Clicks the 'Organisation Parameters' link."""
        self.click(self.organisation_parameters_page)

    def go_to_organisations_and_site_details_page(self) -> None:
        """Clicks the 'Organisation and Site Details' link."""
        self.click(self.organisations_and_site_details_page)

    def go_to_gp_practice_endorsement_page(self) -> None:
        """Clicks the 'GP Practice Endorsement' link."""
        self.click(self.gp_practice_endorsement_page)

    def go_to_upload_nacs_data_bureau_page(self) -> None:
        """Clicks the 'Upload NACS data (Bureau)' link."""
        self.click(self.upload_nacs_data_bureau_page)

    def go_to_bureau_page(self) -> None:
        """Clicks the 'Bureau' link."""
        self.click(self.bureau_page)


class OrganisationSwitchPage(BasePage):
    """
    Page Object Model for Organisation Switch functionality.
    """

    CONTINUE_BUTTON = "button:has-text('Continue')"
    SELECT_ORG_LINK_TEXT = "Select Org"
    RADIO_SELECTOR = "input[type='radio']"

    def __init__(self, page: Page):
        self.page = page

    def get_available_organisation_ids(self)-> list[str]:
        """
        Returns a list of all available organisation radio button IDs.
        """
        radios = self.page.locator(self.RADIO_SELECTOR)
        org_ids = []
        for int in range(radios.count()):
            org_id = radios.nth(int).get_attribute("id")
            if org_id:
                org_ids.append(org_id)
        return org_ids

    def select_organisation_by_id_and_navigate_home(self, org_id: str)-> None:
        """
        Selects the organisation radio button by its ID, clicks Continue,
        navigates to the BCSS Home page, then clicks the 'Select Org' link to return to the organisation selection page.
        Args:
        organisation_id (str): The id of the organisation to be selected.
        """
        self.page.locator(f'#{org_id}').check()
        self.page.get_by_role('button', name='Continue').click()
        self.page.get_by_role('link', name=self.SELECT_ORG_LINK_TEXT).click()

    def switch_between_organisations(self)-> None:
        """
        Switches between all available organisations by their ids.
        """
        org_ids = self.get_available_organisation_ids()
        for org_id in org_ids:
            self.select_organisation_by_id_and_navigate_home(org_id)








