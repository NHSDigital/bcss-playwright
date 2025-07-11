from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LetterLibraryIndexPage(BasePage):
    """Letter Library Index Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Letter Library Index - page locators, methods

    def verify_letter_library_index_title(self) -> None:
        """Verify the Letter Library Index page title is displayed as expected"""
        self.bowel_cancer_screening_page_title_contains_text("Letter Library Index")

    def filter_by_letters_group(self, group_name: str) -> None:
        """
        Selects a letter group from the Letter Type dropdown on the Letter Library Index page.
        Triggers the postback and waits for the page to update.

        Args:
            group_name (str): Visible label of the desired letter group (e.g., 'Supplementary Letters')
        """
        dropdown = self.page.locator("#selLetterType")
        expect(dropdown).to_be_visible()

        # Select the option by its visible label
        dropdown.select_option(label=group_name)

        # Wait for the page to reload—this form triggers a postback
        self.page.wait_for_load_state("load")

        # Optional: wait for something specific to confirm the filter applied
        expect(self.page.locator("text=" + group_name)).to_be_visible()
