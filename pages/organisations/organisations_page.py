from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
from pages.base_page import BasePage
from typing import List

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

class NoOrganisationAvailableError(Exception):
    pass

class OrganisationNotSelectedError(Exception):
    pass

class ContinueButtonNotFoundError(Exception):
    pass


class OrganisationSwitchPage:
    def __init__(self, page: Page):
        self.page = page
        self.radio_selector = "input[name='organisation']"
        self.select_org_link = "a:has-text('Select Organisation')"

    def get_available_organisation_ids(self) -> List[str]:
        self.page.wait_for_selector(self.radio_selector, timeout=10000)
        radios = self.page.locator(self.radio_selector)
        org_ids = [
            org_id for i in range(radios.count())
            if (org_id := radios.nth(i).get_attribute("id")) is not None
        ]
        if len(org_ids) < 2:
            raise NoOrganisationAvailableError("Fewer than two organisations available.")
        return org_ids

    def select_organisation_by_id(self, org_id: str) -> None:
        radio = self.page.locator(f"{self.radio_selector}#{org_id}")
        radio.wait_for(state="visible", timeout=5000)
        radio.check(force=True)

    def select_first_available_organisation(self) -> None:
        for selector in ['#BCS009', '#BCS001']:
            radio = self.page.locator(selector)
            if radio.is_enabled():
                radio.check()
                return
        raise OrganisationNotSelectedError("No available organisation radio buttons to select.")

    def get_selected_organisation_id(self) -> str:
        selected = self.page.locator(f"{self.radio_selector}:checked")
        try:
            selected.wait_for(state="attached", timeout=5000)
        except Exception:
            raise OrganisationNotSelectedError("No organisation is currently selected.")
        org_id = selected.get_attribute("id")
        if not org_id:
            raise OrganisationNotSelectedError("No organisation is currently selected.")
        return org_id

    def click_continue_button(self) -> None:
        try:
            self.page.get_by_role("button", name="Continue").click()
            self.page.wait_for_load_state("networkidle")
        except Exception:
            raise ContinueButtonNotFoundError("Could not find or click the 'Continue' button.")

    def return_to_change_org_page(self) -> None:
        self.page.get_by_role("link", name="Select Org").click()
        self.page.wait_for_url("**/changeorg**", timeout=10000)
        self.page.wait_for_selector(self.radio_selector, timeout=10000)
