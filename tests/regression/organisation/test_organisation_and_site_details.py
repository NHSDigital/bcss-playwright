from ast import Or
import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.organisations import organisations_and_site_details
from pages.organisations.organisations_page import OrganisationsPage
from pages.organisations.organisations_and_site_details import (
    OrganisationsAndSiteDetails,
)
from pages.organisations.list_all_organisations import (
    ListAllOrganisations,
    OrganisationType,
)
from utils.user_tools import UserTools


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the call and recall page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Bureau Staff")

    # Go to call and recall page
    BasePage(page).go_to_organisations_page()


@pytest.mark.regression
@pytest.mark.organisations_users_and_contacts_tests
@pytest.mark.wip
def test_check_list_all_organisations_page(page) -> None:
    """
    Verifies that the 'List All Organisations' page displays correctly and contains expected elements.
    """
    OrganisationsPage(page).go_to_organisations_and_site_details_page()
    OrganisationsAndSiteDetails(page).go_to_list_all_organisations()
    ListAllOrganisations(page).select_organisation_type_option(OrganisationType.ICB)
