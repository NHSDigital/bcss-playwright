from typing import Optional
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.table_util import TableUtils
import logging
from utils.oracle.oracle_specific_functions.organisation_parameters import (
    get_org_parameter_value,
    get_national_parameter_value,
)
from datetime import datetime, timedelta
from utils.calendar_picker import CalendarPicker


class ParametersPage(BasePage):
    """Parameters Page locators, and methods for interacting with the page."""

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
        row_index = self.parameters_table.get_row_index("ID", parameter_id)
        return self.parameters_table.get_cell_value("Lower Value", row_index)

    def get_parameter_upper_value(self, parameter_id: str) -> str:
        """
        Gets the upper value of a parameter from the parameters table.
        Args:
            parameter_id (str): The ID of the parameter to look for.
        Returns:
            str: The upper value of the parameter.
        """
        row_index = self.parameters_table.get_row_index("ID", parameter_id)
        return self.parameters_table.get_cell_value("Upper Value", row_index)

    def click_parameter_id_link(self, parameter_id: str) -> None:
        """Clicks on the parameter ID link in the parameters table.

        Args:
            parameter_id (str): The ID of the parameter to click.
        """
        self.click(self.page.get_by_role("link", name=parameter_id, exact=True))

    def click_add_new_parameter_value_button(self) -> None:
        """Clicks the 'Add new parameter value' button."""
        self.click(self.add_new_parameter_value_button)

    def select_new_parameter_value(self, new_parameter_value: str) -> None:
        """
        Selects a new value from the parameter value input field dropdown.
        Args:
            new_parameter_value (str): The new parameter value to select.
        """
        self.parameter_value_input_field.select_option(label=new_parameter_value)

    def enter_new_parameter_value(self, new_value: str) -> None:
        """
        Enters a new value into the parameter value input field.
        Args:
            new_value (str): The new parameter value to enter.
        """
        self.parameter_value_input_field.fill(new_value)

    def enter_new_parameter_effective_from_date(self, new_date: datetime) -> None:
        """
        Enters a new effective from date into the parameter effective from date input field.
        Args:
            new_date (datetime): The new effective from date to enter.
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            new_date, self.parameter_effective_from_date_input_field
        )

    def enter_new_parameter_effective_from_date_str(self, new_date: str) -> None:
        """
        Enters a new effective from date (string) into the parameter effective from date input field.
        Args:
            new_date (str): The new effective from date (string) to enter.
        """
        self.parameter_effective_from_date_input_field.fill(new_date)

    def enter_parameter_reason(self, reason: str) -> None:
        """
        Enters a reason into the parameter reason input field.
        Args:
            reason (str): The reason for the parameter change.
        """
        self.parameter_reason_input_field.fill(reason)

    def click_save_button(self) -> None:
        """Clicks the 'Save' button."""
        self.click(self.save_button)

    def click_save_button_and_accept_dialog(self) -> None:
        """Clicks the 'Save' button and accepts the confirmation dialog."""
        self.safe_accept_dialog(self.save_button)

    def complete_parameter_page_form(self, criteria: dict) -> None:
        """
        Completes the parameter page form with the provided details.
        Args:
            criteria (dict): A dictionary containing the details to enter into the form.
        """
        for field, value in criteria.items():
            match field:
                case "input value":
                    self.enter_new_parameter_value(value)
                case "select value":
                    self.select_new_parameter_value(value)
                case "effective from date":
                    if isinstance(value, datetime):
                        self.enter_new_parameter_effective_from_date(value)
                    elif isinstance(value, str):
                        self.enter_new_parameter_effective_from_date_str(value)
                case "reason for change":
                    self.enter_parameter_reason(value)

    def get_next_available_date(self) -> datetime:
        """
        Gets the next available date for entering a new parameter value.
        Returns:
            datetime: The next available date for entering a new parameter value.
        """
        most_recent_date = ParameterDetails(self.page).get_most_recent_parameter_date()
        today = datetime.today()
        # If no date found or most recent date is in the past, use today
        base_date = (
            today
            if not most_recent_date or most_recent_date < today
            else most_recent_date
        )
        return base_date + timedelta(days=1)

    def select_screening_centre_parameters_organisation(self, org: str) -> None:
        """
        Selects the organisation for screening centre parameters.
        Args:
            org (str): The organisation to select.
        """
        self.click(self.page.get_by_role("link", name=org))


class ParameterDetails(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)
        self.parameters_table = TableUtils(self.page, "#displayRS")
        self.warning_messages = self.page.locator("th.warningHeader")

    def get_most_recent_parameter_date(self) -> Optional[datetime]:
        """
        Gets the datetime of the most recent parameter value showing in the parameter details table.
        Returns:
            datetime: The datetime of the most recent parameter value showing in the parameter details table.
        """
        num_rows = self.parameters_table.get_row_count()

        most_recent_date = self.parameters_table.get_cell_value(
            "Effective From Date", num_rows
        )
        if most_recent_date == "":
            return None
        return datetime.strptime(most_recent_date, "%d/%m/%Y")

    def get_most_recent_value_of_parameter(self, effective_from_date: datetime) -> str:
        """
        Gets the most value of a parameter from the parameters table.
        Args:
            effective_from_date (datetime): The date to look for.
        Returns:
            str: The most recent value of the parameter.
        """
        date_text = datetime.strftime(effective_from_date, "%d/%m/%Y")

        row_index = self.parameters_table.get_row_index(
            "Effective From Date", date_text
        )
        if row_index is None:
            raise ValueError(f"Parameter with date {date_text} not found in table.")
        return self.parameters_table.get_cell_value("Value", row_index)

    def search_for_warning(self, message: str) -> bool:
        """
        Searches for a warning message in the parameter details page.
        Args:
            message (str): The warning message to search for.
        Returns:
            bool: True if the warning message is found, False otherwise.
        """
        for warning_index in range(self.warning_messages.count()):
            if self.warning_messages.nth(warning_index).inner_text().strip() == message:
                return True
        return False


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
        self.current_value_db = self.get_current_value_from_db()
        self.national_parameter_value = get_national_parameter_value(int(self.param_id))

    def get_current_value_from_db(self) -> str:
        """
        Gets the current value of the parameter from the database.
        Returns:
            str: The current value of the parameter from the database.
        """
        # First check for organisation parameters
        param_df = get_org_parameter_value(int(self.param_id), "23159")
        if not param_df.empty:
            return param_df["val"].values[0]
        else:
            # Then check for screening centre parameters
            param_df2 = get_org_parameter_value(int(self.param_id), "23162")
            if not param_df2.empty:
                return param_df2["val"].values[0]
            else:
                # Otherwise use the national default value
                return get_national_parameter_value(int(self.param_id))
