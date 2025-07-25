from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class AppointmentDetailPage(BasePage):
    """Appointment Detail Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Appointment Detail - page filters
        self.attendance_radio = self.page.get_by_role("radio", name="Attendance")
        self.attended_check_box = self.page.locator("#UI_ATTENDED")
        self.calendar_button = self.page.get_by_role("button", name="Calendar")
        self.save_button = self.page.get_by_role("button", name="Save")

    def check_attendance_radio(self) -> None:
        """Checks the attendance radio button."""
        self.attendance_radio.check()

    def check_attended_check_box(self) -> None:
        """Checks the attended check box."""
        self.attended_check_box.check()

    def click_calendar_button(self) -> None:
        """Clicks the calendar button."""
        self.click(self.calendar_button)

    def click_save_button(self) -> None:
        """Clicks the save button."""
        self.click(self.save_button)

    def verify_text_visible(self, text: str) -> None:
        """Verifies that the specified text is visible on the page."""
        expect(self.page.get_by_text(text)).to_be_visible()

    def wait_for_attendance_radio(self, timeout_duration: float = 30000) -> None:
        """
        Waits for the attendance radio to be visible. Refreshes the page every minute if not visible.
        Default timeout is 30 seconds but this can be changed.

        Args:
            timeout_duration (float): How long to wait in milliseconds.
        """
        elapsed = 0
        refresh_interval = 60000  # 1 minute in milliseconds
        while elapsed < timeout_duration:
            try:
                self.attendance_radio.wait_for(
                    timeout=min(refresh_interval, timeout_duration - elapsed)
                )
                return
            except Exception:
                elapsed += refresh_interval
                if elapsed < timeout_duration:
                    self.page.reload()
        # Final attempt, will raise if not found
        self.attendance_radio.wait_for(
            timeout=(
                timeout_duration - elapsed if timeout_duration - elapsed > 0 else 1000
            )
        )
