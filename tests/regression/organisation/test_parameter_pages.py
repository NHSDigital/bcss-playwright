import pytest
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.organisations import organisations_and_site_details_page
from pages.organisations.organisations_page import OrganisationsPage
from pages.organisations.parameters_page import ParametersPage, Parameter
from pages.organisations.organisations_and_site_details_page import (
    OrganisationsAndSiteDetailsPage,
)
from pages.organisations.list_all_organisations_page import (
    ListAllOrganisationsPage,
    OrganisationType,
)
from pages.organisations.create_organisation_page import CreateOrganisationPage
from pages.organisations.view_organisation_page import ViewOrganisationPage
from pages.organisations.list_all_sites_page import ListAllSitesPage, SiteType
from pages.organisations.create_site_page import CreateSitePage
from utils.user_tools import UserTools
from utils.table_util import TableUtils
from utils.calendar_picker import CalendarPicker
from datetime import datetime, timedelta
import logging
from utils.oracle.oracle_specific_functions.organisation_parameters import (
    get_national_parameter_value,
)


@pytest.mark.wip
def test_parameter_pages_as_hub_manager(page) -> None:
    """
    Test to verify parameter page functionality as a Hub Manager.
    Tests both the organisation and screening centre parameter pages.
    """

    # Given I log in to BCSS "England" as user role "Hub Manager"
    UserTools.user_login(page, "Hub Manager at BCS01")

    # When I navigate to the Organisation Parameters page for my hub
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_organisation_parameters_page()

    # Then I verify that Parameter ID "23" current value matches the value in the database
    parameter_23 = Parameter(page, "23")
    ParametersPage(page).assert_parameter_value_matches_expected(
        parameter_23.param_id, parameter_23.current_value_db
    )

    # When I add a new parameter value for Parameter ID "23" that is less than the Lower Value
    ParametersPage(page).click_parameter_id_link(parameter_23.param_id)
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).enter_new_parameter_details(
        new_value=str(int(parameter_23.lower_value) - 1),
        new_date=datetime.today() + timedelta(days=1),
        reason="Automated Test",
    )

    # When I click the Save button
    # Then I get a confirmation prompt that "contains" "Value must not be less than Lower Value."
    ParametersPage(page).assert_dialog_text(
        "Value must not be less than Lower Value.", True
    )
    ParametersPage(page).click_save_button()

    # When I add a new parameter value for Parameter ID "23" that is greater than the Upper Value
    ParametersPage(page).enter_new_parameter_details(
        new_value=str(int(parameter_23.upper_value) + 1),
        new_date=datetime.today() + timedelta(days=1),
        reason="Automated Test",
    )

    # When I click the Save button
    # Then I get a confirmation prompt that "contains" "Value must not exceed Upper Value."
    ParametersPage(page).assert_dialog_text("Value must not exceed Upper Value.", True)
    ParametersPage(page).click_save_button()

    # When I add a new parameter value for Parameter ID "23" that is empty
    ParametersPage(page).enter_new_parameter_details(
        new_value="",
        new_date=datetime.today() + timedelta(days=1),
        reason="Automated Test",
    )

    national_param_value = get_national_parameter_value(int(parameter_23.param_id))
