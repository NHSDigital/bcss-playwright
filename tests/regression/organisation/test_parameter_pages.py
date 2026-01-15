import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.organisations.organisations_page import (
    OrganisationSwitchPage,
    OrganisationsPage,
)
from pages.organisations.parameters_page import (
    ParametersPage,
    Parameter,
    ParameterDetails,
)
from utils.user_tools import UserTools
from utils.date_time_utils import DateTimeUtils
import logging
from pages.logout.log_out_page import LogoutPage


@pytest.mark.vpn_required
@pytest.mark.regression
def test_parameter_pages(page: Page) -> None:
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
    UserTools.user_login(page, "Hub Manager at BCS01")

    # When I navigate to the Organisation Parameters
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_organisation_parameters_page()

    # Checking integer fields - Parameter 25
    chosen_parameter = Parameter(page, "25")
    ParametersPage(page).assert_parameter_value_matches_expected(
        chosen_parameter.param_id, chosen_parameter.current_value_db
    )
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # When I add a new parameter value that is lower than the allowed minimum
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": str(int(chosen_parameter.lower_value) - 1),
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )

    # Then I get a confirmation prompt that contains "Value must not be less than Lower Value."
    ParametersPage(page).assert_dialog_text(
        "Value must not be less than Lower Value.", True
    )
    ParametersPage(page).click_save_button()

    # When I add a new parameter value that is higher than the allowed maximum
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": str(int(chosen_parameter.upper_value) + 1),
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )

    # Then I get a confirmation prompt that contains "Value must not exceed Upper Value."
    ParametersPage(page).assert_dialog_text("Value must not exceed Upper Value.", True)
    ParametersPage(page).click_save_button()

    # When I add a new parameter value for my parameter that is empty
    ParametersPage(page).click_back_button()
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": "",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then it will default to the national value
    most_recent_value = ParameterDetails(page).get_most_recent_value_of_parameter(
        next_available_date
    )
    assert (
        chosen_parameter.national_parameter_value
    ) == most_recent_value, f"Parameter value does not match national value when empty value entered. Expected {chosen_parameter.national_parameter_value}, got {most_recent_value}"
    logging.info(
        f"[UI ASSERTIONS COMPLETE] Parameter value matches national value when empty value entered:\n Expected Value: {chosen_parameter.national_parameter_value}\n Actual Value: {most_recent_value}"
    )

    # When I add a new parameter value for my parameter that is valid
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": "15",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then the parameter is saved with the correct value
    most_recent_value = ParameterDetails(page).get_most_recent_value_of_parameter(
        next_available_date
    )
    assert (
        most_recent_value == "15"
    ), f"Parameter value does not match the expect value. Expected {chosen_parameter.national_parameter_value}, got {most_recent_value}"
    logging.info(
        f"[UI ASSERTIONS COMPLETE] Parameter value matches expected value:\n Expected Value: 15\n Actual Value: {most_recent_value}"
    )

    # When I add a new parameter value for my parameter that is of an incorrect type
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": "test incorrect type",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then a warning message appears on the following page
    assert ParameterDetails(page).search_for_warning(
        "The update has failed, your changes have not been saved"
    )
    assert ParameterDetails(page).search_for_warning(
        "Parameter value is of the wrong data type"
    )
    logging.info(
        "[UI ASSERTIONS COMPLETE] Warning messages displayed for incorrect parameter value type"
    )

    # When I go pack to "Organisation Parameters" page
    ParametersPage(page).click_back_button()
    ParametersPage(page).click_back_button()

    # Checking Yes/No fields - Parameter 199
    chosen_parameter = Parameter(page, "199")
    ParametersPage(page).assert_parameter_value_matches_expected(
        chosen_parameter.param_id, chosen_parameter.current_value_db
    )
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # When I select "Yes" for my parameter
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "select value": "Yes",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then it will save the value as "Y"
    most_recent_value = ParameterDetails(page).get_most_recent_value_of_parameter(
        next_available_date
    )
    assert (
        most_recent_value == "Y"
    ), f"Parameter value not saved as 'Y' when 'Yes' selected. Got {most_recent_value}"
    logging.info(
        f"[UI ASSERTIONS COMPLETE] Parameter value saved as 'Y' when 'Yes' selected:\n Expected Value: Y\n Actual Value: {most_recent_value}"
    )

    # When I select "No" for my parameter
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "select value": "No",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then it will save the value as "N"
    most_recent_value = ParameterDetails(page).get_most_recent_value_of_parameter(
        next_available_date
    )
    assert (
        most_recent_value == "N"
    ), f"Parameter value not saved as 'N' when 'No' selected. Got {most_recent_value}"
    logging.info(
        f"[UI ASSERTIONS COMPLETE] Parameter value saved as 'N' when 'No' selected:\n Expected Value: N\n Actual Value: {most_recent_value}"
    )

    # When I select "Yes" for my parameter but do not enter a reason
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "select value": "Yes",
            "effective from date": next_available_date,
            "reason for change": "",
        }
    )

    # Then I get a confirmation prompt that contains "The fields 'Parameter Value', 'Effective From Date' and 'Reason For Change or Addition' are mandatory."
    ParametersPage(page).assert_dialog_text(
        "The fields 'Parameter Value', 'Effective From Date' and 'Reason For Change or Addition' are mandatory.",
        True,
    )
    ParametersPage(page).click_save_button()

    # When I go back to the "Organisation Parameters" page
    ParametersPage(page).click_back_button()
    ParametersPage(page).click_back_button()

    # Checking string fields - Parameter 182
    chosen_parameter = Parameter(page, "182")
    ParametersPage(page).assert_parameter_value_matches_expected(
        chosen_parameter.param_id, chosen_parameter.current_value_db
    )
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # When I add a new parameter value for my parameter that is valid
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": "Valid String Test",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then the parameter is saved with the correct value
    most_recent_value = ParameterDetails(page).get_most_recent_value_of_parameter(
        next_available_date
    )
    assert (
        most_recent_value == "Valid String Test"
    ), f"Parameter value does not match the expect value. Expected 'Valid String Test', got {most_recent_value}"
    logging.info(
        f"[UI ASSERTIONS COMPLETE] Parameter value matches expected value:\n Expected Value: 'Valid String Test'\n Actual Value: {most_recent_value}"
    )

    # When I navigate to the Screening Centre Parameters
    ParametersPage(page).click_main_menu_link()
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_screening_centre_parameters_page()
    ParametersPage(page).select_screening_centre_parameters_organisation("BCS001")

    # Checking time fields - Parameter 28
    chosen_parameter = Parameter(page, "28")
    ParametersPage(page).assert_parameter_value_matches_expected(
        chosen_parameter.param_id, chosen_parameter.current_value_db
    )
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # When I add a value for my parameter that is lower than the allowed minimum
    next_available_date = ParametersPage(page).get_next_available_date()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": DateTimeUtils.add_time_to_time_string(
                chosen_parameter.lower_value, -1
            ),
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then a warning message appears on the following page
    assert ParameterDetails(page).search_for_warning(
        "The update has failed, your changes have not been saved"
    )
    assert ParameterDetails(page).search_for_warning(
        "Parameter value is not within the defined range of values"
    )
    logging.info(
        "[UI ASSERTIONS COMPLETE] Warning messages displayed for out-of-bounds time parameter value"
    )

    # When I add a value for my parameter that is higher than the allowed maximum
    ParametersPage(page).click_back_button()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": DateTimeUtils.add_time_to_time_string(
                chosen_parameter.upper_value, 1
            ),
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then a warning message appears on the following page
    assert ParameterDetails(page).search_for_warning(
        "The update has failed, your changes have not been saved"
    )
    assert ParameterDetails(page).search_for_warning(
        "Parameter value is not within the defined range of values"
    )
    logging.info(
        "[UI ASSERTIONS COMPLETE] Warning messages displayed for out-of-bounds time parameter value"
    )

    # When I add a valid value for my parameter
    ParametersPage(page).click_back_button()
    ParametersPage(page).click_add_new_parameter_value_button()
    ParametersPage(page).complete_parameter_page_form(
        {
            "input value": "10:00",
            "effective from date": next_available_date,
            "reason for change": "Automated Test",
        }
    )
    ParametersPage(page).click_save_button_and_accept_dialog()

    # Then the parameter is saved with the correct value
    most_recent_value = ParameterDetails(page).get_most_recent_value_of_parameter(
        next_available_date
    )
    assert (
        most_recent_value == "10:00"
    ), f"Parameter value does not match the expect value. Expected '10:00', got {most_recent_value}"
    logging.info(
        f"[UI ASSERTIONS COMPLETE] Parameter value matches expected value:\n Expected Value: '10:00'\n Actual Value: {most_recent_value}"
    )

    # Finally, I log out
    LogoutPage(page).log_out()


@pytest.mark.parameter_212
def test_parameter_212(page: Page) -> None:
    """
    Test viewing and adding new values for Parameter ID "212" across different user roles.
    1. Log in as "Screening Centre Manager" and verify inability to edit new parameter value.
    2. Switch to "Hub Manager" and verify inability to edit new parameter value.
    3. Switch to "BCSS Support - SC" and verify ability to edit new parameter value.
    4. Switch to "BCSS Support - HUB" and verify ability to edit new parameter value.
    5. Log out.
    """
    # Given I log in to BCSS "England" as user role "Screening Centre Manager"
    UserTools.user_login(page, "Screening Centre Manager at BCS001")

    # When I navigate to the Organisation Parameters page
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_organisation_parameters_page()

    # Then I can see that Parameter ID "212" has the correct value from the database
    chosen_parameter = Parameter(page, "212")
    ParametersPage(page).assert_parameter_value_matches_expected(
        chosen_parameter.param_id, chosen_parameter.current_value_db
    )

    # I am able to view Parameter ID "212" as a Screening Centre Manager
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # I "cannot" add a new parameter value
    assert ParametersPage(
        page
    ).add_new_parameter_value_button.is_hidden(), "Add New Parameter Value button is visible, but should be hidden for Screening Centre Manager"
    logging.info(
        "[UI ASSERTIONS COMPLETE] 'Add New Parameter Value' button is hidden for Screening Centre Manager"
    )

    # When I switch users to BCSS "England" as user role "Hub Manager"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    UserTools.user_login(page, "Hub Manager at BCS01")

    # Then I go to the Screening Centre Parameters page
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_screening_centre_parameters_page()
    ParametersPage(page).select_screening_centre_parameters_organisation("BCS001")

    # I am able to view Parameter ID "212" as a hub manager
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # I "cannot" add a new parameter value
    assert ParametersPage(
        page
    ).add_new_parameter_value_button.is_hidden(), "Add New Parameter Value button is visible, but should be hidden for Hub Manager"
    logging.info(
        "[UI ASSERTIONS COMPLETE] 'Add New Parameter Value' button is hidden for Hub Manager"
    )

    # When I switch users to BCSS "England" as user role "BCSS Support - SC"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    UserTools.user_login(page, "BCSS Support - SC at BCS001")

    # Then I go to the Organisation Parameters page
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_organisation_parameters_page()

    # I am able to view Parameter ID "212" as a support user
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # I "can" add a new parameter value
    assert ParametersPage(
        page
    ).add_new_parameter_value_button.is_visible(), "Add New Parameter Value button is hidden, but should be visible for BCSS Support - SC"
    logging.info(
        "[UI ASSERTIONS COMPLETE] 'Add New Parameter Value' button is visible for BCSS Support - SC"
    )

    # When I switch users to BCSS "England" as user role "BCSS Support - HUB"
    LogoutPage(page).log_out(close_page=False)
    BasePage(page).go_to_log_in_page()
    UserTools.user_login(page, "BCSS Support - HUB")
    OrganisationSwitchPage(page).select_organisation_by_id("BCS01")
    OrganisationSwitchPage(page).click_continue()

    # Then i go to organisation parameters page
    BasePage(page).go_to_organisations_page()
    OrganisationsPage(page).go_to_screening_centre_parameters_page()
    ParametersPage(page).select_screening_centre_parameters_organisation("BCS001")

    # I am able to view Parameter ID "212" as a support user
    ParametersPage(page).click_parameter_id_link(chosen_parameter.param_id)

    # I "can" add a new parameter value
    assert ParametersPage(
        page
    ).add_new_parameter_value_button.is_visible(), "Add New Parameter Value button is hidden, but should be visible for BCSS Support - HUB"
    logging.info(
        "[UI ASSERTIONS COMPLETE] 'Add New Parameter Value' button is visible for BCSS Support - HUB"
    )

    # Finally, I log out
    LogoutPage(page).log_out()
