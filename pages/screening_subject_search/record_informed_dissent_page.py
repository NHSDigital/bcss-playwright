from playwright.sync_api import Page
from pages.base_page import BasePage
from datetime import datetime
from utils.calendar_picker import CalendarPicker


class RecordInformedDissentPage(BasePage):
    """Record Informed Dissent Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Record informed Dissent - page locators
        self.notes_field = self.page.locator("#UI_NOTES_TEXT")
        self.date_confimed_input = self.page.locator("#UI_CEASING_CONFIRM_DATE")
        self.confirm_cease_button = self.page.get_by_role(
            "button", name="Confirm Cease"
        )

    def fill_notes_field(self, note: str) -> None:
        """
        Fill the notes field.
        Args:
            note (str): The note to add.
        """
        self.notes_field.fill(note)

    def enter_date_confirmed(self, date: datetime) -> None:
        """
        Enter date confirmed
        Args:
            date (datetime): The date to enter
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            date, self.date_confimed_input
        )

    def click_confirm_cease_button(self) -> None:
        """Click the 'Confirm Cease' button."""
        self.safe_accept_dialog(self.confirm_cease_button)
