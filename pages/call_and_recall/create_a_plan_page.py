from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.table_util import TableUtils


class CreateAPlanPage(BasePage):
    """Create a Plan page locators and methods to interact with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Call and Recall - page links
        self.set_all_button = self.page.get_by_role("link", name="Set all")
        self.daily_invitation_rate_field = self.page.get_by_placeholder(
            "Enter daily invitation rate"
        )
        self.weekly_invitation_rate_field = self.page.get_by_placeholder(
            "Enter weekly invitation rate"
        )
        self.update_button = self.page.get_by_role("button", name="Update")
        self.confirm_button = self.page.get_by_role("button", name="Confirm")
        self.save_button = self.page.get_by_role("button", name="Save")
        self.note_field = self.page.get_by_placeholder("Enter note")
        self.save_note_button = self.page.locator("#saveNote").get_by_role(
            "button", name="Save"
        )
        # Create A Plan Table Locators
        self.weekly_invitation_rate_field_on_table = self.page.locator(
            "#invitationRateField"
        )
        self.invitations_sent_value = self.page.locator(
            "#invitationPlan > tbody > tr:nth-child(1) > td:nth-child(8)"
        )
        self.resulting_position_value = self.page.locator(
            "#invitationPlan > tbody > tr:nth-child(1) > td:nth-child(9)"
        )

        # Initialize TableUtils for different tables
        self.create_a_plan_table = TableUtils(page, "#invitationPlan")

    def click_set_all_button(self) -> None:
        """Clicks the Set all button to set all values"""
        self.click(self.set_all_button)

    def fill_daily_invitation_rate_field(self, value: str) -> None:
        """Fills the daily invitation rate field with the given value"""
        self.daily_invitation_rate_field.fill(value)

    def fill_weekly_invitation_rate_field(self, value) -> None:
        """Fills the weekly invitation rate field with the given value"""
        self.weekly_invitation_rate_field.fill(value)

    def click_update_button(self) -> None:
        """Clicks the Update button to save any changes"""
        self.click(self.update_button)

    def click_confirm_button(self) -> None:
        """Clicks the Confirm button"""
        self.click(self.confirm_button)

    def click_save_button(self) -> None:
        """Clicks the Save button"""
        self.click(self.save_button)

    def fill_note_field(self, value) -> None:
        """Fills the note field with the given value"""
        self.note_field.fill(value)

    def click_save_note_button(self) -> None:
        """Clicks the Save note button"""
        self.click(self.save_note_button)

    def verify_create_a_plan_title(self) -> None:
        """Verifies the Create a Plan page title"""
        self.bowel_cancer_screening_page_title_contains_text("View a plan")

    def verify_weekly_invitation_rate_for_weeks(
        self, start_week: int, end_week: int, expected_weekly_rate: str
    ) -> None:
        """
        Verifies that the weekly invitation rate is correctly calculated and displayed for the specified range of weeks.

        Args:
        start_week (int): The starting week of the range.
        end_week (int): The ending week of the range.
        expected_weekly_rate (str): The expected weekly invitation rate.
        """
        # Get the current weekly invitation rate for the starting week
        weekly_invitation_rate = self.page.query_selector_all(
            "css:nth-child(" + str(start_week) + ") .text"
        )[0].inner_text()
        assert (
            weekly_invitation_rate == expected_weekly_rate
        ), f"Expected weekly invitation rate '{expected_weekly_rate}' for week {start_week} but got '{weekly_invitation_rate}'"

        # Verify the rate for the specified range of weeks
        for week in range(start_week + 1, end_week + 1):
            weekly_rate_locator = f".week-{week} .text"
            assert (
                self.page.query_selector_all(weekly_rate_locator)[0].inner_text()
                == expected_weekly_rate
            ), f"Week {week} invitation rate should be '{expected_weekly_rate}', but found '{self.page.query_selector_all(weekly_rate_locator)[0].inner_text()}'"

    def increment_invitation_rate_and_verify_changes(self) -> None:
        """
        Increments the invitation rate by 1, then verifies that both the 'Invitations Sent' and 'Resulting Position' have increased by 1.
        """
        # Get the current value of the Weekly Invitation Rate field
        current_value = int(
            self.create_a_plan_table.get_cell_value("Invitation Rate", 0)
        )
        # Increments by 1, fills the field with the new value, and Tabs out of the field
        new_value = str(current_value + 1)
        locator = self.weekly_invitation_rate_field_on_table
        locator.fill(new_value)
        locator.press("Tab")

        # Verifies 'Invitations Sent' has increased by 1
        initial_invitations_sent = int(self.invitations_sent_value.inner_text())
        assert (
            int(self.invitations_sent_value.inner_text())
            == initial_invitations_sent + 1
        ), "Invitations Sent did not increase by 1."

        # Verifies 'Resulting Position' has increased by 1
        initial_resulting_position = int(self.resulting_position_value.inner_text())
        assert (
            int(self.resulting_position_value.inner_text())
            == initial_resulting_position - 1
        ), "Resulting Position did not decrease by 1."
