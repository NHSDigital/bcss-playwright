from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
from enum import Enum
from utils.calendar_picker import CalendarPicker


class ContactWithPatientPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Contact With Patient - Page Locators
        self.contact_direction_dropdown = page.locator("#UI_DIRECTION")
        self.contact_made_between_Patient_and_dropdown = page.locator("#UI_CALLER_ID")
        self.calendar_button = page.get_by_role("button", name="Calendar")
        self.time_from_text_field = page.get_by_role("textbox", name="Start Time")
        self.time_to_text_field = page.get_by_role("textbox", name="End Time")
        self.discussion_record_text_field = page.get_by_role("textbox", name="Discussion Record")
        self.outcome_dropdown = page.locator("##UI_OUTCOME")
        self.save_button = page.get_by_role("button", name="Save")

    def select_direction_dropdown_option(self, direction: str) -> None:
        self.contact_direction_dropdown.select_option(label=direction)

    def select_callerid_dropdown_option(self, callerid: str) -> None:
        self.contact_made_between_Patient_and_dropdown.select_option(label=callerid)

    def click_calendar_button(self) -> None:
        self.click(self.calendar_button)

    def enter_start_time(self, start_time: str) -> None:
        self.time_from_text_field.fill(start_time)

    def enter_end_time(self, end_time: str) -> None:
        self.time_to_text_field.fill(end_time)

    def enter_discussion_record_text(self, value: str) -> None:
        self.discussion_record_text_field.fill(value)

    def select_outcome_dropdown_option(self, outcome: str) -> None:
        self.outcome_dropdown.select_option(label=outcome)

    def click_save_button(self) -> None:
        self.click(self.save_button)


