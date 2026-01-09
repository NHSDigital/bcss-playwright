from playwright.sync_api import Page
from pages.base_page import BasePage
from typing import List
from utils.table_util import TableUtils
import logging
from utils.oracle.oracle_specific_functions.organisation_parameters import (
    get_org_parameter_value,
)
from datetime import datetime
from utils.calendar_picker import CalendarPicker


class ParametersPage(BasePage):
    """Organisations Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.parameters_table = TableUtils(self.page, "#displayRS")
        self.parameters_output_table = TableUtils(self.page, "#displayRS")
        self.add_new_parameter_value_button = self.page.get_by_role(
            "button", name="Add new parameter value"
        )
        self.parameter_value_input_field = self.page.locator("#A_C_VALUE")
        self.parameter_effective_from_date_input_field = self.page.locator(
            "#A_C_START_DATE"
        )
        self.parameter_reason_input_field = self.page.locator("#A_C_AUDIT_REASON")
        self.save_button = self.page.get_by_role("button", name="Save")
        self.row_index = None

    def get_current_value_of_parameter(self, parameter_id: str) -> str:
        """
        Gets the current value of a parameter from the parameters table.

        Args:
            parameter_id (str): The ID of the parameter to look for.
        Returns:
            str: The current value of the parameter.
        """
        row_index = self.parameters_table.get_row_index("ID", parameter_id)
        if row_index is None:
            raise ValueError(
                f"Parameter ID {parameter_id} not found in parameters table."
            )
        return self.parameters_table.get_cell_value("Current Value", row_index)

    def assert_parameter_value_matches_expected(
        self, parameter_id: str, expected_value: str
    ) -> None:
        """
        Asserts that the current value of a parameter matches the expected value.
        Args:
            parameter_id (str): The ID of the parameter to look for.
            expected_value (str): The expected value of the parameter.
        """
        actual_value = self.get_current_value_of_parameter(parameter_id)
        assert (
            actual_value == expected_value
        ), f"Parameter ID {parameter_id} value mismatch: expected {expected_value}, got {actual_value}"
        logging.info(
            f"Parameter ID {parameter_id} value matches expected: {expected_value}"
        )

    def get_parameter_lower_value(self, parameter_id: str) -> str:
        """
        Gets the lower value of a parameter from the parameters table.
        Args:
            parameter_id (str): The ID of the parameter to look for.
        Returns:
            str: The lower value of the parameter.
        """
        if self.row_index is None:
            self.row_index = self.parameters_table.get_row_index("ID", parameter_id)
        return self.parameters_table.get_cell_value("Lower Value", self.row_index)

    def get_parameter_upper_value(self, parameter_id: str) -> str:
        """
        Gets the upper value of a parameter from the parameters table.
        Args:
            parameter_id (str): The ID of the parameter to look for.
        Returns:
            str: The upper value of the parameter.
        """
        if self.row_index is None:
            self.row_index = self.parameters_table.get_row_index("ID", parameter_id)
        return self.parameters_table.get_cell_value("Upper Value", self.row_index)

    def click_parameter_id_link(self, parameter_id: str) -> None:
        """Clicks on the parameter ID link in the parameters table.

        Args:
            parameter_id (str): The ID of the parameter to click.
        """
        self.click(self.page.get_by_role("link", name=parameter_id, exact=True))

    def click_add_new_parameter_value_button(self) -> None:
        """Clicks the 'Add new parameter value' button."""
        self.click(self.add_new_parameter_value_button)

    def enter_new_parameter_value(self, new_value: str) -> None:
        """Enters a new value into the parameter value input field."""
        self.parameter_value_input_field.fill(new_value)

    def enter_new_parameter_effective_from_date(self, new_date: datetime) -> None:
        """Enters a new effective from date into the parameter effective from date input field."""
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            new_date, self.parameter_effective_from_date_input_field
        )

    def enter_parameter_reason(self, reason: str) -> None:
        """Enters a reason into the parameter reason input field."""
        self.parameter_reason_input_field.fill(reason)

    def click_save_button(self) -> None:
        """Clicks the 'Save' button."""
        self.click(self.save_button)

    def click_save_button_and_accept_dialog(self) -> None:
        """Clicks the 'Save' button and accepts the confirmation dialog."""
        self.safe_accept_dialog(self.save_button)

    def enter_new_parameter_details(
        self, new_value: str, new_date: datetime, reason: str
    ) -> None:
        """
        Enters new parameter details.
        Args:
            new_value (str): The new value for the parameter.
            new_date (datetime): The effective from date for the new parameter value.
            reason (str): The reason for the change.
        """
        self.enter_new_parameter_value(new_value)
        self.enter_new_parameter_effective_from_date(new_date)
        self.enter_parameter_reason(reason)


class Parameter:
    """Class representing a parameter with its attributes."""

    def __init__(
        self,
        page: Page,
        param_id: str,
    ):
        self.page = page
        self.param_id = param_id
        self.lower_value = ParametersPage(self.page).get_parameter_lower_value(
            self.param_id
        )
        self.upper_value = ParametersPage(self.page).get_parameter_upper_value(
            self.param_id
        )
        self.current_value = ParametersPage(self.page).get_current_value_of_parameter(
            self.param_id
        )
        self.current_value_db = get_org_parameter_value(int(self.param_id), "23159")[
            "val"
        ].values[0]
