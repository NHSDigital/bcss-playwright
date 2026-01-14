import pytest
from numpy.ma.testutils import assert_equal
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from pages.organisations import organisations_and_site_details_page
from pages.organisations.organisations_page import OrganisationsPage
from pages.organisations.parameters_page import (
    ParametersPage,
    Parameter,
    ParameterDetails,
)
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
from pages.logout.log_out_page import LogoutPage


class TestParameterChanges:

    @pytest.fixture(autouse=True)
    def setup(self, page):
        self.page = page

    @pytest.mark.wip
    def test_parameter_pages(self) -> None:
        """
        Test various interactions on the Organisation Parameters page, including adding new parameter values
        and validating their correctness against database values.
        1. Log in as "Hub Manager"
        2. Navigate to Organisation Parameters page
        3. Validate integer parameter (ID 25)
        4. Validate Yes/No parameter (ID 199)
        5. Validate string parameter (ID 182)
        6. Navigate to Screening Centre Parameters page
        7. Validate time parameter (ID 28)
        8. Log out
        """

        # Given I log in to BCSS "England" as user role "Hub Manager"
        UserTools.user_login(self.page, "Hub Manager at BCS01")

        # When I navigate to the Organisation Parameters
        BasePage(self.page).go_to_organisations_page()
        OrganisationsPage(self.page).go_to_organisation_parameters_page()

        # Checking integer fields - Parameter 25
        chosen_parameter = Parameter(self.page, "25")
        self.check_chosen_parameter_correct_in_db(chosen_parameter)
        ParametersPage(self.page).click_parameter_id_link(chosen_parameter.param_id)

        # When I add a new parameter value for Parameter ID "25" that is lower than the allowed minimum
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": str(int(chosen_parameter.lower_value) - 1),
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )

        # Then I get a confirmation prompt that contains "Value must not be less than Lower Value."
        ParametersPage(self.page).assert_dialog_text(
            "Value must not be less than Lower Value.", True
        )
        ParametersPage(self.page).click_save_button()

        # When I add a new parameter value for Parameter ID "25" that is higher than the allowed maximum
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": str(int(chosen_parameter.upper_value) + 1),
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )

        # Then I get a confirmation prompt that contains "Value must not exceed Upper Value."
        ParametersPage(self.page).assert_dialog_text(
            "Value must not exceed Upper Value.", True
        )
        ParametersPage(self.page).click_save_button()

        # When I add a new parameter value for my parameter that is empty
        ParametersPage(self.page).click_back_button()
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": "",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then it will default to the national value
        most_recent_value = ParameterDetails(
            self.page
        ).get_most_recent_value_of_parameter(next_available_date)
        assert (
            chosen_parameter.national_parameter_value
        ) == most_recent_value, f"Parameter value does not match national value when empty value entered. Expected {chosen_parameter.national_parameter_value}, got {most_recent_value}"
        logging.info(
            f"[UI ASSERTIONS COMPLETE] Parameter value matches national value when empty value entered:\n Expected Value: {chosen_parameter.national_parameter_value}\n Actual Value: {most_recent_value}"
        )

        # When I add a new parameter value for my parameter that is valid
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": "15",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then the parameter is saved with the correct value
        most_recent_value = ParameterDetails(
            self.page
        ).get_most_recent_value_of_parameter(next_available_date)
        assert (
            most_recent_value == "15"
        ), f"Parameter value does not match the expect value. Expected {chosen_parameter.national_parameter_value}, got {most_recent_value}"
        logging.info(
            f"[UI ASSERTIONS COMPLETE] Parameter value matches expected value:\n Expected Value: 15\n Actual Value: {most_recent_value}"
        )

        # When I add a new parameter value for my parameter that is of an incorrect type
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": "test incorrect type",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then a warning message appears on the following page
        assert ParameterDetails(self.page).search_for_warning(
            "The update has failed, your changes have not been saved"
        )
        assert ParameterDetails(self.page).search_for_warning(
            "Parameter value is of the wrong data type"
        )
        logging.info(
            "[UI ASSERTIONS COMPLETE] Warning messages displayed for incorrect parameter value type"
        )

        # WHen I go pack to rgw "Organisation Parameters" page
        ParametersPage(self.page).click_back_button()
        ParametersPage(self.page).click_back_button()

        # Checking Yes/No fields - Parameter 199
        chosen_parameter = Parameter(self.page, "199")
        self.check_chosen_parameter_correct_in_db(chosen_parameter)
        ParametersPage(self.page).click_parameter_id_link(chosen_parameter.param_id)

        # When I select "Yes" for my parameter
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "select value": "Yes",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then it will save the value as "Y"
        most_recent_value = ParameterDetails(
            self.page
        ).get_most_recent_value_of_parameter(next_available_date)
        assert (
            most_recent_value == "Y"
        ), f"Parameter value not saved as 'Y' when 'Yes' selected. Got {most_recent_value}"
        logging.info(
            f"[UI ASSERTIONS COMPLETE] Parameter value saved as 'Y' when 'Yes' selected:\n Expected Value: Y\n Actual Value: {most_recent_value}"
        )

        # When I select "No" for my parameter
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "select value": "No",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then it will save the value as "N"
        most_recent_value = ParameterDetails(
            self.page
        ).get_most_recent_value_of_parameter(next_available_date)
        assert (
            most_recent_value == "N"
        ), f"Parameter value not saved as 'N' when 'No' selected. Got {most_recent_value}"
        logging.info(
            f"[UI ASSERTIONS COMPLETE] Parameter value saved as 'N' when 'No' selected:\n Expected Value: N\n Actual Value: {most_recent_value}"
        )

        # When I select "Yes" for my parameter but do not enter a reason
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "select value": "Yes",
                "effective from date": next_available_date,
                "reason for change": "",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()
        # Then I get a confirmation prompt that contains "The fields 'Parameter Value', 'Effective From Date' and 'Reason For Change or Addition' are mandatory."
        ParametersPage(self.page).assert_dialog_text(
            "The fields 'Parameter Value', 'Effective From Date' and 'Reason For Change or Addition' are mandatory.",
            True,
        )

        # When I go back to the "Organisation Parameters" page
        ParametersPage(self.page).click_back_button()
        ParametersPage(self.page).click_back_button()

        # Checking string fields - Parameter 182
        chosen_parameter = Parameter(self.page, "182")
        self.check_chosen_parameter_correct_in_db(chosen_parameter)
        ParametersPage(self.page).click_parameter_id_link(chosen_parameter.param_id)

        # When I add a new parameter value for my parameter that is valid
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": "Valid String Test",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then the parameter is saved with the correct value
        most_recent_value = ParameterDetails(
            self.page
        ).get_most_recent_value_of_parameter(next_available_date)
        assert (
            most_recent_value == "Valid String Test"
        ), f"Parameter value does not match the expect value. Expected 'Valid String Test', got {most_recent_value}"
        logging.info(
            f"[UI ASSERTIONS COMPLETE] Parameter value matches expected value:\n Expected Value: 'Valid String Test'\n Actual Value: {most_recent_value}"
        )

        # When I navigate to the Screening Centre Parameters
        ParametersPage(self.page).click_main_menu_link()
        BasePage(self.page).go_to_organisations_page()
        OrganisationsPage(self.page).go_to_screening_centre_parameters_page()
        ParametersPage(self.page).select_screening_centre_parameters_organisation(
            "BCS001"
        )

        # Checking time fields - Parameter 28
        chosen_parameter = Parameter(self.page, "28")
        self.check_chosen_parameter_correct_in_db(chosen_parameter)
        ParametersPage(self.page).click_parameter_id_link(chosen_parameter.param_id)

        # When I add a value for my parameter that is lower than the allowed minimum
        next_available_date = ParametersPage(self.page).get_next_available_date()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": chosen_parameter.get_add_to_time_value(
                    chosen_parameter.lower_value, -1
                ),
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then a warning message appears on the following page
        assert ParameterDetails(self.page).search_for_warning(
            "The update has failed, your changes have not been saved"
        )
        assert ParameterDetails(self.page).search_for_warning(
            "Parameter value is not within the defined range of values"
        )
        logging.info(
            "[UI ASSERTIONS COMPLETE] Warning messages displayed for out-of-bounds time parameter value"
        )

        # When I add a value for my parameter that is higher than the allowed maximum
        ParametersPage(self.page).click_back_button()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": chosen_parameter.get_add_to_time_value(
                    chosen_parameter.upper_value, 1
                ),
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then a warning message appears on the following page
        assert ParameterDetails(self.page).search_for_warning(
            "The update has failed, your changes have not been saved"
        )
        assert ParameterDetails(self.page).search_for_warning(
            "Parameter value is not within the defined range of values"
        )
        logging.info(
            "[UI ASSERTIONS COMPLETE] Warning messages displayed for out-of-bounds time parameter value"
        )

        # When I add a valid value for my parameter
        ParametersPage(self.page).click_back_button()
        ParametersPage(self.page).click_add_new_parameter_value_button()
        ParametersPage(self.page).complete_parameter_page_form(
            {
                "input value": "10:00",
                "effective from date": next_available_date,
                "reason for change": "Automated Test",
            }
        )
        ParametersPage(self.page).click_save_button_and_accept_dialog()

        # Then the parameter is saved with the correct value
        most_recent_value = ParameterDetails(
            self.page
        ).get_most_recent_value_of_parameter(next_available_date)
        assert (
            most_recent_value == "10:00"
        ), f"Parameter value does not match the expect value. Expected '10:00', got {most_recent_value}"
        logging.info(
            f"[UI ASSERTIONS COMPLETE] Parameter value matches expected value:\n Expected Value: '10:00'\n Actual Value: {most_recent_value}"
        )

        # Finally, I log out
        LogoutPage(self.page).log_out()

    def test_parameter_212(self) -> None:
        """ """
        # Given I log in to BCSS "England" as user role "Screening Centre Manager"
        UserTools.user_login(self.page, "Screening Centre Manager at BCS001")

        # When I navigate to the Organisation Parameters page
        BasePage(self.page).go_to_organisations_page()
        OrganisationsPage(self.page).go_to_organisation_parameters_page()

        # Then I can see that Parameter ID "212" has the correct value from the database
        chosen_parameter = Parameter(self.page, "212")
        self.check_chosen_parameter_correct_in_db(chosen_parameter)

        # I am able to view Parameter ID "212" as a Screening Centre Manager
        ParametersPage(self.page).click_parameter_id_link(chosen_parameter.param_id)

        # I "cannot" add a new parameter value
        assert ParametersPage(
            self.page
        ).add_new_parameter_value_button.is_hidden(), "Add New Parameter Value button is visible, but should be hidden for Screening Centre Manager"
        logging.info(
            "[UI ASSERTIONS COMPLETE] 'Add New Parameter Value' button is hidden for Screening Centre Manager"
        )

        # When I switch users to BCSS "England" as user role "Hub Manager"
        LogoutPage(self.page).log_out(close_page=False)
        BasePage(self.page).go_to_log_in_page()
        UserTools.user_login(self.page, "Hub Manager at BCS01")

        # Then i go to screening centre parameters page
        # I am able to view Parameter ID "212" as a hub manager
        # I "cannot" add a new parameter value

        # When I switch users to BCSS "England" as user role "BCSS Support - SC"

        LogoutPage(self.page).log_out()

    def check_chosen_parameter_correct_in_db(
        self, chosen_parameter: "Parameter"
    ) -> None:
        """
        Checks that the chosen parameter's current value matches the expected value from the database.
        Args:
            chosen_parameter (Parameter): The parameter to check.
        """
        ParametersPage(self.page).assert_parameter_value_matches_expected(
            chosen_parameter.param_id, chosen_parameter.current_value_db
        )
