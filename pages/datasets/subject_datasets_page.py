from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class SubjectDatasetsPage(BasePage):
    """Subject Datasets Page locators, and methods for interacting with the page"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Subject datasets page locators
        self.colonoscopy_show_dataset_button = (
            self.page.locator("div")
            # Note: The "(1 Dataset)" part of the line below may be dynamic and may change based on the actual dataset count.
            .filter(
                has_text="Colonoscopy Assessment (1 Dataset) Show Dataset"
            ).get_by_role("link")
        )
        self.investigation_show_dataset_button = (
            self.page.locator("div")
            # Note: The "(1 Dataset)" part of the line below may be dynamic and may change based on the actual dataset count.
            .filter(has_text="Investigation (1 Dataset) Show Dataset").get_by_role(
                "link"
            )
        )

    def click_colonoscopy_show_datasets(self) -> None:
        """Clicks on the 'Show Dataset' button for the Colonoscopy Assessment row on the Subject Datasets Page."""
        self.click(self.colonoscopy_show_dataset_button)

    def click_investigation_show_datasets(self) -> None:
        """Clicks on the 'Show Dataset' button for the Investigation row on the Subject Datasets Page."""
        self.click(self.investigation_show_dataset_button)

    def expect_text_to_be_visible(self, text: str) -> None:
        """
        This method is designed to expect a text to be visible on the page.
        It checks if the given text is visible.

        Args:
            text (str): The text to check for visibility.
        """
        expect(self.page.get_by_text(text).nth(1)).to_be_visible()
