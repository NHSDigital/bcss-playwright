from playwright.sync_api import Page
from pages.base_page import BasePage


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

    def select_referral_dropdown_option(self, value: str) -> None:
        """
        Select a given option from the Referral dropdown.

        Args:
            value (str): The value of the option you want to select
        """
        self.referral_dropdown.select_option(value)

    def select_first_practitioner(self) -> None:
        """Select the first option from the Practitioner dropdown."""
        self.practitioner_dropdown.select_option(index=1)

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
