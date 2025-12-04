from playwright.sync_api import Page
from pages.base_page import BasePage
from datetime import datetime
from utils.calendar_picker import CalendarPicker


class DischargeFromSurveillancePage(BasePage):
    """Discharge From Surveillance Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Locators
        self.date_decision_made_input_field = self.page.locator("#UI_OTHER_DATE")
        self.screening_consultant_lookup_link = self.page.locator(
            "#UI_CONSULTANT_PIO_SELECT_LINK"
        )
        self.screening_pracitioner_dropdown = self.page.locator(
            "#UI_SCREENING_PRACTITIONER"
        )
        self.notes_field = self.page.locator("#UI_NOTES")
        self.save_button = self.page.get_by_role("button", name="Save")

    def enter_date_decision_made(self, date: datetime) -> None:
        """
        Enter a date into the 'Date Decision Made' field
        Args:
            date (datetime): the date to enter.
        """
        CalendarPicker(self.page).calendar_picker_ddmmyyyy(
            date, self.date_decision_made_input_field
        )

    def select_screening_consultant_from_index(self, index: int) -> None:
        """
        This method is designed to select a screening consultant from the screening consultant lookup options.
        It clicks on the screening consultant lookup link and selects the given option by index.
        Args:
            index (int): The index of the option to select from the screening consultant lookup options.
        """
        self.click(self.screening_consultant_lookup_link)
        select_locator = self.page.locator('select[id^="UI_RESULTS_"]:visible')
        select_locator.first.wait_for(state="visible")
        # Find all option elements inside the select and click the one at the given index
        option_elements = select_locator.first.locator("option")
        option_elements.nth(index).wait_for(state="visible")
        self.click(option_elements.nth(index))

    def select_screening_pracitioner_from_index(self, index: int) -> None:
        """
        Selects a screening pracitioner.
        Args:
            index (int): The index of the option to select
        """
        self.screening_pracitioner_dropdown.select_option(index=index)

    def fill_notes_field(self, note: str) -> None:
        """
        Enter a note into the notes field
        Args:
            note (str): The note to enter.
        """
        self.notes_field.fill(note)

    def click_save_button(self) -> None:
        """Click on the 'Save' button."""
        self.safe_accept_dialog(self.save_button)

    def complete_discharge_from_surveillance_form(
        self, include_screening_consultant: bool
    ) -> None:
        """
        Completes the discharge from surveillance form.
        Args:
            include_screening_consultant (bool): Whether or not to include a screening consultant in the form
        """
        self.enter_date_decision_made(datetime.today())
        if include_screening_consultant:
            self.select_screening_consultant_from_index(-1)
        self.select_screening_pracitioner_from_index(1)
        self.fill_notes_field("Notes for subject being discharged")
        self.click_save_button()
        self.page.wait_for_timeout(
            1000
        )  # Timeout to allow subject to be updated on the DB.
