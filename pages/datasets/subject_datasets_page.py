from playwright.sync_api import Page
from pages.base_page import BasePage


class SubjectDatasetsPage(BasePage):
    """
    This class contains locators and methods to interact with the Subject Datasets page.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Subject datasets page locators
        self.colonoscopy_show_dataset_button = self.page.get_by_role(role="link", name="Show Dataset")

    def click_colonoscopy_show_datasets(self) -> None:
        self.click(self.colonoscopy_show_dataset_button)
