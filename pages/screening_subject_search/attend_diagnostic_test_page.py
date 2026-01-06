from playwright.sync_api import Page
from pages.base_page import BasePage


class AttendDiagnosticTestPage(BasePage):
    """Attend Diagnostic Test Page locators and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Advance Diagnostic Test - page locators
        self.actual_type_of_test_dropdown = self.page.locator(
            "#UI_CONFIRMED_TYPE_OF_TEST"
        )
        self.intended_extent_dropdown = self.page.locator(
            "select[id^='UI_INTENDED_EXTENT']"
        )
        self.data_table_rows = self.page.locator("#topTable > tbody > tr")
        self.calendar_button = self.page.get_by_role("button", name="Calendar")
        self.save_button = self.page.get_by_role("button", name="Save")

    def select_actual_type_of_test_dropdown_option(self, text: str) -> None:
        """Select the actual type of test from the dropdown."""
        self.actual_type_of_test_dropdown.select_option(label=text)

    def click_calendar_button(self) -> None:
        """Click the calendar button to open the calendar picker."""
        self.click(self.calendar_button)

    def click_save_button(self) -> None:
        """Click the 'Save' button."""
        self.click(self.save_button)

    def confirm_proposed_type_of_test(
        self, field_name: str, expected_value: str
    ) -> None:
        """
        Confirm that the proposed type of test matches the expected value.
        Args:
            field_name (str): The name of the field to check.
            expected_value (str): The expected value to compare against.
        """
        actual_value = self.get_field_value_by_label(field_name)
        assert (
            actual_value is not None and actual_value.lower() == expected_value.lower()
        ), f"{field_name} is not as expected [Expected: '{expected_value}', Actual: '{actual_value}']"

    def get_field_value_by_label(self, row_label: str) -> str | None:
        """
        Get the value of a field based on its label.
        Args:
            row_label (str): The label of the row to retrieve the value for.
        Returns:
            str | None: The value of the field, or None if not found.
        """
        if row_label.lower() == "actual type of test":
            return self.get_actual_type_of_test()
        elif row_label.lower() == "intended extent":
            return self.get_intended_extent()
        else:
            return self.get_table_text_by_label(row_label)

    def get_actual_type_of_test(self) -> str | None:
        """
        Get the selected actual type of test from the dropdown.
        Returns:
            str | None: The selected actual type of test, or None if not found.
        """
        try:
            selected_option = self.actual_type_of_test_dropdown.locator(
                "option:checked"
            )
            text = selected_option.inner_text(timeout=2000)
            return text.strip() if text else None
        except Exception:
            return None

    def is_intended_extent_dropdown_visible(self) -> bool:
        """
        Check if the intended extent dropdown is visible.
        Returns:
            bool: True if visible, False otherwise.
        """
        try:
            return self.intended_extent_dropdown.is_visible(timeout=2000)
        except Exception:
            return False

    def get_intended_extent(self) -> str | None:
        """
        Get the selected intended extent from the dropdown.
        Returns:
            str | None: The selected intended extent, or None if not found.
        """
        if self.is_intended_extent_dropdown_visible():
            try:
                selected_option = self.intended_extent_dropdown.locator(
                    "option:checked"
                )
                text = selected_option.inner_text(timeout=2000)
                return text.strip() if text else None
            except Exception:
                return None
        else:
            return None

    def get_table_text_by_label(self, row_label: str) -> str | None:
        """
        Get the text from the data table based on the provided row label.
        Args:
            row_label (str): The label of the row to retrieve the text for.
        Returns:
            str | None: The text corresponding to the label, or None if not found.
        """
        row_count = self.data_table_rows.count()
        for i in range(row_count):
            row = self.data_table_rows.nth(i)
            cells = row.locator("td")
            if cells.count() >= 2:
                label_text = cells.nth(0).inner_text(timeout=1000).strip()
                if row_label.lower() == label_text.lower():
                    value_text = cells.nth(1).inner_text(timeout=1000).strip()
                    return value_text
        return None
