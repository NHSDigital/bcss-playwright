from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from datetime import datetime
from utils.calendar_picker import CalendarPicker
from utils.table_util import TableUtils


class BatchListPage(BasePage):
    """Batch List Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Batch List - page filters
        self.id_filter = self.page.locator("#batchIdFilter")
        self.type_filter = self.page.locator("#batchTypeFilter")
        self.original_filter = self.page.locator("#originalBatchIdFilter")
        self.event_code_filter = self.page.locator("#eventCodeFilter")
        self.description_filter = self.page.locator("#eventDescriptionFilter")
        self.batch_split_by_filter = self.page.locator("#splitByFilter")
        self.screening_centre_filter = self.page.locator("#screeningCentreFilter")
        self.count_filter = self.page.locator("#countFilter")
        self.table_data = self.page.locator("td")
        self.batch_successfully_archived_msg = self.page.locator(
            'text="Batch Successfully Archived and Printed"'
        )
        self.deadline_calendar_picker = self.page.locator("i")
        self.deadline_date_filter = self.page.get_by_role("cell", name="").get_by_role(
            "textbox"
        )
        self.deadline_date_filter_with_input = self.page.locator(
            "input.form-control.filter.filtering"
        )
        self.deadline_date_clear_button = self.page.get_by_role("cell", name="Clear")

    def verify_batch_list_page_title(self, text) -> None:
        """Verify the Batch List page title is displayed as expected"""
        self.bowel_cancer_screening_page_title_contains_text(text)

    def verify_table_data(self, value) -> None:
        """Verify the table data is displayed as expected"""
        expect(self.table_data.filter(has_text=value)).to_be_visible()

    def enter_id_filter(self, search_text: str) -> None:
        """Enter text in the ID filter and press Enter"""
        self.id_filter.fill(search_text)
        self.id_filter.press("Enter")

    def enter_type_filter(self, search_text: str) -> None:
        """Enter text in the Type filter and press Enter"""
        self.type_filter.fill(search_text)
        self.type_filter.press("Enter")

    def enter_original_filter(self, search_text: str) -> None:
        """Enter text in the Original filter and press Enter"""
        self.original_filter.fill(search_text)
        self.original_filter.press("Enter")

    def enter_event_code_filter(self, search_text: str) -> None:
        """Enter text in the Event Code filter and press Enter"""
        self.event_code_filter.fill(search_text)
        self.event_code_filter.press("Enter")

    def enter_description_filter(self, search_text: str) -> None:
        """Enter text in the Description filter and press Enter"""
        self.description_filter.fill(search_text)
        self.description_filter.press("Enter")

    def enter_batch_split_by_filter(self, search_text: str) -> None:
        """Enter text in the 'Batch Split By' filter and press Enter"""
        self.batch_split_by_filter.fill(search_text)
        self.batch_split_by_filter.press("Enter")

    def enter_screening_centre_filter(self, search_text: str) -> None:
        """Enter text in the Screening Centre filter and press Enter"""
        self.screening_centre_filter.fill(search_text)
        self.screening_centre_filter.press("Enter")

    def enter_count_filter(self, search_text: str) -> None:
        """Enter text in the Count filter and press Enter"""
        self.count_filter.fill(search_text)
        self.count_filter.press("Enter")

    def enter_deadline_date_filter(self, date: datetime) -> None:
        """Enter a date in the Deadline Date filter and press Enter"""
        self.click(self.deadline_calendar_picker)
        CalendarPicker(self.page).v2_calendar_picker(date)

    def clear_deadline_filter_date(self) -> None:
        """Clear the date in the Deadline Date filter"""
        self.click(self.deadline_calendar_picker)
        self.click(self.deadline_date_clear_button)

    def verify_deadline_date_filter_input(self, expected_text: str) -> None:
        expect(self.deadline_date_filter_with_input).to_have_value(expected_text)

    def open_letter_batch(
        self, batch_type: str, status: str, level: str, description: str
    ) -> None:
        """
        Finds and opens the batch row based on type, status, level, and description.
        Args:
            batch_type (str): The type of the batch (e.g., "Original").
            status (str): The status of the batch (e.g., "Open").
            level (str): The level of the batch (e.g., "S1").
            description (str): The description of the batch (e.g., "Pre-invitation (FIT)").
        """
        # Step 1: Match the row using nested filters, one per column value
        row = (
            self.page.locator("table tbody tr")
            .filter(has=self.page.locator("td", has_text=batch_type))
            .filter(has=self.page.locator("td", has_text=status))
            .filter(has=self.page.locator("td", has_text=level))
            .filter(has=self.page.locator("td", has_text=description))
        )

        # Step 2: Click the "View" link in the matched row
        view_link = row.locator(
            "a"
        )  # Click the first link in the row identified in step 1
        expect(view_link).to_be_visible()
        view_link.click()


class ActiveBatchListPage(BatchListPage):
    """Active Batch List Page locators, and methods for interacting with the Active Batch List page"""

    def __init__(self, page):
        super().__init__(page)

    def assert_column_present(self, column_name: str) -> None:
        """Asserts that the specified column is present in the table header."""
        headers = list(
            TableUtils(self.page, "table#batchList").get_table_headers().values()
        )
        assert (
            column_name in headers
        ), f"Column '{column_name}' not found in table headers"

    def assert_column_sortable(self, column_name: str) -> None:
        """Asserts that the specified column is marked as sortable in the UI."""
        sort_locator = self.page.locator(
            "table#batchList thead tr:first-child th span.dt-column-title",
            has_text=column_name,
        )
        assert (
            sort_locator.count() > 0
        ), f"Sortable header not found for column '{column_name}'"
        assert (
            sort_locator.first.get_attribute("role") == "button"
        ), f"Column '{column_name}' is not sortable"

    def assert_column_filterable(self, column_name: str) -> None:
        """Asserts that the specified column has a filter control in the second header row."""
        table = TableUtils(self.page, "table#batchList")
        column_index = (
            table.get_column_index(column_name) - 1
        )  # Convert 1-based to 0-based

        filter_locator = (
            self.page.locator("table#batchList thead tr:nth-child(2) th")
            .nth(column_index)
            .locator("input, select, div.input-group")
        )
        assert (
            filter_locator.count() > 0
        ), f"Filter control not found for column '{column_name}'"

    def assert_batch_table_visible(self) -> None:
        """Asserts that the batch list table is present and rendered."""
        expect(self.page.locator("table#batchList")).to_be_visible()

    def select_first_active_batch(self) -> None:
        """Clicks the first batch ID link in the active batch list."""
        first_batch_link = self.page.locator("table#batchList tbody tr td.id a").first
        assert first_batch_link.count() > 0, "No active batch links found"
        first_batch_link.click()

    def is_batch_present(self, batch_type: str) -> bool:
        """Checks if a batch of the given type exists in the active batch list."""
        locator = self.page.locator(f"table#batchList tbody tr td", has_text=batch_type)
        return locator.count() > 0

    def prepare_batch(self, batch_type: str) -> None:
        """Finds and clicks the Prepare button for the specified batch type."""
        row = (
            self.page.locator("table#batchList tbody tr")
            .filter(has=self.page.locator("td", has_text=batch_type))
            .first
        )

        prepare_button = row.locator("a", has_text="Prepare").first
        expect(prepare_button).to_be_visible()
        prepare_button.click()

        # Optional: wait for row to disappear
        expect(row).not_to_be_visible(timeout=5000)


class ArchivedBatchListPage(BatchListPage):
    """Archived Batch List Page locators, and methods for interacting with the Archived Batch List page"""

    def __init__(self, page):
        super().__init__(page)
