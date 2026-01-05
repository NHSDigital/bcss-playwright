from playwright.sync_api import Page
from pages.screening_subject_search.postpone_episode_page import PostponeEpisodePage
from datetime import datetime
from utils.calendar_picker import CalendarPicker


class PostponeSurveillanceEpisodePage(PostponeEpisodePage):
    """Postpone Surveillance Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Postpone Surveillance Episode page - page locators
        self.change_surveillance_due_date_field = self.page.locator(
            "#A_C_SurveillanceScreeningDueDate"
        )

    def enter_date_in_change_surveillance_due_date_field(self, date: datetime) -> None:
        """
        Enters a date in the Change Surveillance Due Date field.
        Args:
            date (datetime): The date to enter in the field.
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            date, self.change_surveillance_due_date_field
        )

    def postpone_surveillance_episode(self, criteria: dict) -> None:
        """
        Postpone surveillance episode with given criteria.
        Args:
            criteria (dict): A dictionary containing the following keys:
                - reason (str): The reason for postponing the episode.
                - clinical reason (str): The clinical reason for postponing the episode.
                - notes (str): Notes regarding the postponement.
                - change surveillance due date (datetime): The new surveillance due date.
                - reason for date change (str): The reason for changing the date.
        """
        self.select_reason_dropdown_option(criteria["reason"])
        self.select_clinical_reason_dropdown_option(criteria["clinical reason"])
        self.enter_notes(criteria["notes"])
        self.enter_date_in_change_surveillance_due_date_field(
            criteria["change surveillance due date"]
        )
        self.select_reason_for_date_change_dropdown_option(
            criteria["reason for date change"]
        )
        self.click_postpone_episode_button()
