from playwright.sync_api import Page
from pages.base_page import BasePage
from datetime import datetime
from utils.calendar_picker import CalendarPicker


class HandoverIntoSymptomaticCarePage(BasePage):
    """
    HandoverIntoSymptomaticCarePage class for interacting with the 'Handover Into Symptomatic Care' page elements.
    """

    def __init__(self, page: Page):
        self.page = page
        self.referral_dropdown = self.page.get_by_label("Referral")
        self.calendar_button = self.page.get_by_role("button", name="Calendar")
        self.consultant_link = self.page.locator("#UI_NS_CONSULTANT_PIO_SELECT_LINK")
        self.practitioner_dropdown = self.page.locator("#UI_SCREENING_PRACTITIONER")
        self.notes_textbox = self.page.get_by_role("textbox", name="Notes")
        self.save_button = self.page.get_by_role("button", name="Save")
        self.cease_from_program_dropdown = self.page.locator(
            "#UI_CEASE_FROM_PROGRAM_ID"
        )
        self.mdt_date_field = self.page.locator("#UI_MDT_DATE")
        self.site_dropdown = self.page.locator("#UI_NS_SITE_SELECT_LINK")

    def select_referral_dropdown_option(self, value: str) -> None:
        """
        Select a given option from the Referral dropdown.

        Args:
            value (str): The value of the option you want to select
        """
        self.referral_dropdown.select_option(value)

    def select_practitioner_from_index(self, practitioner_index: int) -> None:
        """
        Select the first option from the Practitioner dropdown.
        Args:
            practitioner_index (int): The index of the practitioner to select.
        """
        self.practitioner_dropdown.select_option(index=practitioner_index)

    def click_calendar_button(self) -> None:
        """Click the calendar button to open the calendar picker."""
        self.click(self.calendar_button)

    def select_consultant(self, value: str) -> None:
        """
        Select a consultant from the consultant dropdown using the given value.

        Args:
        value (str): The value attribute of the consultant option to select.
        """
        self.consultant_link.click()
        option_locator = self.page.locator(f'[value="{value}"]:visible')
        option_locator.wait_for(state="visible")
        self.click(option_locator)

    def fill_notes(self, notes: str) -> None:
        """
        Fill the 'Notes' textbox with the provided text.

        Args:
        notes (str): The text to enter into the notes textbox.
        """
        self.notes_textbox.click()
        self.notes_textbox.fill(notes)

    def click_save_button(self) -> None:
        """Click the save button to save the changes."""
        self.safe_accept_dialog(self.save_button)

    def select_cease_from_program(self, cease: bool) -> None:
        """
        Select an option from the Cease from Program dropdown.

        Args:
            cease (bool): True to cease from program, False otherwise
        """
        value = "Yes" if cease else "No"
        self.cease_from_program_dropdown.select_option(value)

    def enter_mdt_date(self, date: datetime) -> None:
        """
        Enters a date into the 'MDT Date' field
        Args:
            date (datetime): The date to enter.
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(date, self.mdt_date_field)

    def select_site_dropdown_option_index(self, index: int) -> None:
        """
        Select a given option from the site dropdown.

        Args:
            value (str): The value of the option you want to select
        """
        self.click(self.site_dropdown)
        select_locator = self.page.locator('select[id^="UI_RESULTS_"]:visible')
        select_locator.first.wait_for(state="visible")

        # Find all option elements inside the select and click the one at the given index
        option_elements = select_locator.first.locator("option")
        option_elements.nth(index).wait_for(state="visible")
        self.click(option_elements.nth(index))

    def fill_with_cancer_details(self) -> None:
        """
        Complete the Handover into Symptomatic Care form with the cancer details scenario:
            MDT Date: Today
            Site: Last option
            Screening Practitioner: 1st option
            Note: Handover notes for Cancer scenario
        """
        self.enter_mdt_date(datetime.today())
        self.select_site_dropdown_option_index(-1)
        self.select_practitioner_from_index(1)
        self.fill_notes("Handover notes for Cancer scenario")
        self.click_save_button()
        self.page.wait_for_timeout(500)  # Timeout to allow subject to update in the DB.
