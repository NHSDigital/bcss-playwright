from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.table_util import TableUtils


class LetterLibraryIndexPage(BasePage):
    """Letter Library Index Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.table_utils = TableUtils(page, "#displayRS")
        # Letter Library Index - page locators, methods

        self.letter_library_index_table = page.locator("#displayRS")
        self.define_supplementary_letter_button = page.locator(
            "input.HeaderButtons[value='Define Supplementary Letter']"
        )

    def verify_letter_library_index_title(self) -> None:
        """Verify the Letter Library Index page title is displayed as expected"""
        self.bowel_cancer_screening_page_title_contains_text("Letter Library Index")

    def filter_by_letters_group(self, group_name: str) -> None:
        """
        Selects a letter group from the Letter Type dropdown on the Letter Library Index page.
        Triggers the postback and waits for the page to update.

        Args:
            group_name (str): Visible label of the desired letter group. Must be one of:
                - 'Discharge Letters (Patient)'
                - 'Discharge Letters (GP)'
                - 'Discharge Notification Cards To GP Practice'
                - '30 Day Questionnaire'
                - 'Surveillance Selection'
                - 'Invitation Letters'
                - 'MDT Referral Letter to GP'
                - 'Practitioner Clinic Letters'
                - 'Reminder Letters'
                - 'Result Letters (Patient)'
                - 'Result Communications (GP)'
                - 'Retest Letters'
                - 'Supplementary Letters'
                - 'Bowel Scope Hub Letters'
                - 'Genetic Service Letters'
        """
        dropdown = self.page.locator("#selLetterType")
        expect(dropdown).to_be_visible()

        # Select the option by its visible label
        dropdown.select_option(label=group_name)

        # Wait for the page to reload—this form triggers a postback
        self.page.wait_for_load_state("load")

    def filter_by_event_code(self, event_code: str) -> None:
        """
        Filters the letter library index by event code using the textbox input.

        Args:
            event_code (str): The event code to filter the list (e.g., 'S1')
        """
        event_code_input = self.page.get_by_role(
            "textbox", name="Enter text to filter the list"
        )
        expect(event_code_input).to_be_visible()
        event_code_input.click()
        event_code_input.fill(event_code)
        event_code_input.press("Enter")

        # Optional: wait for the filtered list to update
        self.page.wait_for_timeout(500)  # tweak or replace with smart wait

    def click_first_letter_code_link_in_table(self) -> None:
        """Clicks the first link from the Letter Library Index table."""
        self.table_utils.click_first_link_in_column("Code")

    def click_define_supplementary_letter_button(self) -> None:
        """
        Clicks the 'Define Supplementary Letter' button

        Raises:
            AssertionError: If the button is not visible or interactive
        """
        button = self.define_supplementary_letter_button
        expect(button).to_be_visible()
        button.click()

    def define_supplementary_letter(
        self,
        description: str = "Define Letter",
        destination_id: str = "12057",
        priority_id: str = "12016",
        signatory: str = "signatory",
        job_title: str = "job title",
        paragraph_text: str = "body text"
    ) -> None:
        """
        Fills out the form to define a supplementary letter and confirms save via modal.

        Args:
            description (str): Letter description
            destination_id (str): Dropdown option for destination
            priority_id (str): Dropdown option for priority
            signatory (str): Signatory name
            job_title (str): Signatory's job title
            paragraph_text (str): Main body text of the letter
        """
        self.page.locator('input[name="A_C_LETT_DESC"]').fill(description)
        self.page.locator("#A_C_DESTINATION_ID").select_option(destination_id)
        self.page.locator("#A_C_PRIORITY_ID").select_option(priority_id)
        self.page.locator("#A_C_SIGNATORY").fill(signatory)
        self.page.locator("#A_C_JOB_TITLE").fill(job_title)
        self.page.locator("#A_C_PARAGRAPH_1").fill(paragraph_text)

        # Handle the modal popup when saving
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_role("button", name="Save").click()


