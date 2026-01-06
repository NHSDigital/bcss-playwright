from playwright.sync_api import Page
from pages.base_page import BasePage


class CreateNewAnalyserPage(BasePage):
    """Create New Analyser page locators and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Create New Analyser - page locators, methods
        self.analyser_code_textbox = page.get_by_role("textbox", name="Analyser Code")
        self.analyser_name_textbox = page.get_by_role("textbox", name="Analyser Name")
        self.serial_number_textbox = page.get_by_role("textbox", name="Serial Number")
        self.start_date_textbox = page.get_by_role("textbox", name="Start Date")
        self.software_version_textbox = page.get_by_role(
            "textbox", name="Software Version"
        )
        self.software_start_date_textbox = page.locator("#softwareStartDate")
        self.software_start_time_textbox = page.locator("#softwarestarttime")
        self.end_date_textbox = page.get_by_role("textbox", name="End Date")
        self.lookup_link = page.get_by_role("link", name="Lookup")
        self.save_button = page.get_by_role("button", name="Save")

    def verify_create_new_analyser_title(self) -> None:
        """Verify the Create New Analyser page title is displayed correctly."""
        self.bowel_cancer_screening_page_title_contains_text("Create New Analyser")

    def select_analyser_from_lookup(self, analyser_type: str) -> None:
        """Presses lookup link and selects the Analyser Type specified"""
        self.lookup_link.click()
        self.page.locator(
            f"input[type='radio'][onclick*=\"'{analyser_type}'\"]"
        ).check()
